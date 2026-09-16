"""La vue principale : boucle de jeu, dessin, clavier.

Volontairement minimale pour l'instant : elle sert à faire tourner et à tester
le moteur de collisions. Le HUD définitif ira dans ``ui.py``, le compteur de
vies et les cicatrices dans ``vies.py``, les maîtres dans ``maitre.py`` — ce
fichier appellera simplement ces modules quand ils existeront.

Ordre d'une image :

    1. clavier     -> intentions du chat
    2. chat        -> vitesses (calculer_deplacement)
    3. collisions  -> déplacement réel, murs, plateformes, mortels, poussables
    4. jeu         -> vies, progression, dessin
"""

import math
import random

import arcade

from game import constantes as C
from game import niveau as module_niveau
from game.chat import Chat
from game.collisions import MoteurCollisions
from game.effets import Effets
from game.ambiance import Ambiance
from game.entites import Pousseur
from game.audio import Audio

#: distance a laquelle le chat peut attraper un objet devant lui
PORTEE_ACTION = 14.0

#: libelles affiches au-dessus du chat quand une action est possible
LIBELLES = {
    "scalpel": "Le scalpel", "couteau": "Le couteau", "seringue": "La seringue",
    "defibrillateur": "Le defibrillateur", "medicaments": "La pharmacie",
    "patient": "Le patient malade", "poison": "Le poison", "aquarium": "L'aquarium",
    "cable": "Le cable", "marmite": "La marmite", "gamelle_vide": "La gamelle",
    "vieille": "La charentaise", "enfant": "L'enfant", "chef": "Le chef",
    "chat_gris": "Un autre chat", "panier_linge": "Le buffet a linge",
    "maquillage": "Le maquillage", "lit_baldaquin": "Le lit a baldaquin",
    "cordelette": "Le fil dentaire", "griffures": "Grimper au mur",
    "fenetre_ouverte": "La fenetre", "prise": "La prise", "gaz": "Le gaz",
    "four": "Le four", "bougie": "La bougie", "verre_casse": "Le verre casse",
    "plante": "La plante", "papillon": "Le papillon", "pelote": "La pelote de laine",
    "somniferes": "Les somniferes", "sac": "Le sac de croquettes",
}


class VueJeu(arcade.View):
    def __init__(self, numero_niveau: int = 1):
        super().__init__()
        self.numero_niveau = numero_niveau
        self.vies = C.VIES_DEPART
        self.debug = False
        self.message = ""
        self.minuteur_message = 0.0

        self.niveau = None
        self.chat = None
        self.collisions = None
        self.pause_mort = 0.0        # temps d'affichage du chat allonge
        self.effets = Effets()
        self.toupie = 0.0            # le chat tourne sur lui-meme (faux piege)
        self.camera_active = False
        self.champ_x = self.champ_y = 0.0
        self.champ_rayon = 160
        self.horde = arcade.SpriteList()   # cent chats qui deferlent (niveau 2)
        self.horde_lancee = False
        self.flammes = []                  # jets de feu de la cuisine (niveau 5)
        self.vie_barre = C.VIE_MAX         # niveau 5 : barre a vider en mangeant des piments
        self.piments = arcade.SpriteList()
        self.satiete = 0.0                 # niveau 1 : barre a remplir en se gavant
        self.croquettes = arcade.SpriteList()
        self.distributeur = None
        self.doodle = False                # niveau 1 : mode Doodle Jump vertical
        self.camera_y = 0.0
        self.camera_doodle = None
        self.gui_camera = None
        self.doodle_base_y = 0.0
        self.transition = 0.0              # ecran de lore entre les niveaux
        self.audio = Audio()
        self.audio.demarrer_ambiance()
        self.ralenti = 0.0           # court ralenti a la mort
        self.flash = 0.0             # flash blanc a la mort
        self.rejouer = False         # au niveau 7, mourir fait recommencer
        self.gamelle = None          # la zone du piege a armer
        self.sortie = None           # niveau 7 : la ou il faut arriver vivant
        self.termine = False         # le jeu est fini
        self.charger_niveau(numero_niveau)

    # ------------------------------------------------------------------
    def charger_niveau(self, numero: int) -> None:
        self.numero_niveau = numero
        self.niveau = module_niveau.charger(numero)

        x, y = self.niveau.depart_chat
        self.chat = Chat(x, y)

        # Les métadonnées du niveau peuvent couper un réflexe dès le départ.
        for reflexe in self.niveau.reflexes_coupes:
            setattr(self.chat, f"reflexe_{reflexe}", False)

        self.doodle = getattr(self.niveau, "doodle", False)
        if self.doodle:
            self._generer_doodle()

        self.collisions = MoteurCollisions(
            self.chat,
            murs=self.niveau.murs,
            plateformes=self.niveau.plateformes,
            mortels=self.niveau.mortels,
            poussables=self.niveau.poussables,
            zones=self.niveau.zones,
            largeur_niveau=self.niveau.largeur,
            rampes=getattr(self.niveau, "rampes", []),
        )

        self.gamelle = self.niveau.trouver_zone("gamelle")
        self.sortie = self.niveau.trouver_zone("sortie")

        # niveau 5 : les piments a manger (la barre de vie a vider)
        self.vie_barre = C.VIE_MAX
        self.piments = arcade.SpriteList()
        for pos in getattr(self.niveau, "piments", []):
            x, y = self.niveau.point(pos)
            piment = module_niveau._image("piment", x, y_bas=y)
            if piment is None:
                piment = arcade.Sprite(arcade.Texture.create_empty("p", (20, 28), (215, 45, 40)),
                                       center_x=x, center_y=y + 14)
            piment.repop = 0.0
            self.piments.append(piment)

        # niveau 1 : les croquettes et le distributeur poses par ancres.
        # En mode Doodle Jump, tout est deja genere par _generer_doodle.
        if not self.doodle:
            self.satiete = 0.0
            self.croquettes = arcade.SpriteList()
            for pos in getattr(self.niveau, "croquettes", []):
                x, y = self.niveau.point(pos)
                croq = module_niveau._image("catfood", x, y_bas=y)
                if croq is None:
                    croq = arcade.Sprite(arcade.Texture.create_empty("c", (18, 24), (150, 96, 50)),
                                         center_x=x, center_y=y + 12)
                self.croquettes.append(croq)
            self.distributeur = None
            nom_distri = getattr(self.niveau, "distributeur", "")
            if nom_distri:
                x, y = self.niveau.point(nom_distri)
                self.distributeur = module_niveau._image("distributeur", x, y_bas=y)

        # l'animation du piege mortel (aquarium, cable) posee sur sa zone
        self.piege_frames = []
        nom_anime = getattr(self.niveau, "piege_anime", "")
        if nom_anime and self.gamelle is not None:
            i = 0
            while (C.DOSSIER_IMAGES / "decor" / f"{nom_anime}_{i}.png").is_file():
                self.piege_frames.append(arcade.load_texture(C.DOSSIER_IMAGES / "decor" / f"{nom_anime}_{i}.png"))
                i += 1

        if self.niveau.famille:
            self.transition = 5.0
        if getattr(self, "audio", None) is not None:
            self.audio.jouer_musique(self.numero_niveau)
        self._construire_faux_pieges()

        # la fille (niveau 3) : elle poursuit et rejette le chat
        # niveau 5 : les jets de flammes des cuisinieres (position, phase)
        self.flammes = []
        for i, pos in enumerate(getattr(self.niveau, "flammes", [])):
            x, y = self.niveau.point(pos)
            self.flammes.append({"x": x, "y": y, "phase": i * 0.7})

        # niveau 4 : le champ de camera de l'influenceur, qui suit le chat en retard
        self.camera_active = getattr(self.niveau, "camera", False)
        self.champ_x, self.champ_y = self.chat.center_x, self.chat.center_y

        self.fille = None
        if getattr(self.niveau, "fille", None) is not None:
            from game.entites import Fille
            x, y = self.niveau.fille
            self.fille = Fille(x, y)

        # le chat noir (niveau 2) : la sortie, E dessus fait griller une vie
        self.chat_noir = None
        if getattr(self.niveau, "chat_noir", None) is not None:
            from game.entites import ChatNoir
            x, y = self.niveau.chat_noir
            self.chat_noir = ChatNoir(x, y)

        self.medecin = None
        if self.niveau.docteur and self.gamelle is not None:
            from game.medecin import Medecin
            self.medecin = Medecin(self.gamelle.center_x, sol=self.gamelle.bottom)

        # le fond peint : c'est lui, le decor
        self.fond = None
        if self.niveau.fond:
            texture = arcade.load_texture(C.DOSSIER_IMAGES / self.niveau.fond)
            self.fond = arcade.Sprite(texture, scale=self.niveau.largeur / texture.width)
            self.fond.center_x = self.niveau.largeur / 2
            self.fond.center_y = self.niveau.hauteur / 2
        self.ambiance = Ambiance(self.niveau)

        # les pousseurs : des entites qui bousculent le chat loin du danger
        self.pousseurs = arcade.SpriteList()
        for spec in self.niveau.pousseurs:
            (xg, yg) = self.niveau.point(spec["min"])
            (xd, yd) = self.niveau.point(spec["max"])
            self.pousseurs.append(Pousseur(
                (xg + xd) / 2, min(xg, xd), max(xg, xd), yg,
                image=spec.get("image", "chat_gris"),
                vitesse=spec.get("vitesse", 2.2),
                force=spec.get("force", 16)))
        if self.niveau.aide:
            self.afficher(self.niveau.aide)

    def _generer_doodle(self) -> None:
        """Construit la tour du Doodle Jump : une colonne d etageres a grimper.

        Les plateformes generees deviennent la geometrie du niveau (le moteur de
        collisions n est pas utilise en mode doodle : la physique est maison).
        Une graine fixe garantit une tour toujours franchissable.
        """
        W = C.LARGEUR_FENETRE
        rng = random.Random(7)
        plats = arcade.SpriteList(use_spatial_hash=True)
        self.croquettes = arcade.SpriteList()

        tex_planche = None
        chemin_planche = C.DOSSIER_IMAGES / "decor" / "planche.png"
        if chemin_planche.is_file():
            tex_planche = arcade.load_texture(chemin_planche)

        def barre(cx, cy, larg, haut=18, couleur=(150, 104, 66)):
            if tex_planche is not None:                # jolie planche en bois etiree
                p = arcade.Sprite(tex_planche, center_x=cx, center_y=cy)
                p.width = larg
                p.height = haut
            else:                                      # secours : une barre unie
                tex = arcade.Texture.create_empty(f"_plat_{int(cx)}_{int(cy)}",
                                                  (int(larg), int(haut)), couleur)
                p = arcade.Sprite(tex, center_x=cx, center_y=cy)
            p.vx = 0.0                  # etagere fixe par defaut
            return p

        base_y = 90
        base = barre(W / 2, base_y, W, 26, (120, 86, 56))          # sol de depart
        plats.append(base)
        self.doodle_base_y = base.top

        y = base_y
        sens = -1                       # on demarre en partant vers la gauche
        mobile_precedente = False
        for _ in range(C.DOODLE_NB_PLATEFORMES):
            y += rng.randint(C.DOODLE_ESPACE_MIN, C.DOODLE_ESPACE_MAX)
            larg = rng.choice((130, 155, 180))
            # zigzag centre sur l ecran : une etagere a gauche du milieu, la
            # suivante a droite, pour forcer des sauts alternes gauche/droite
            sens = -sens
            x = W / 2 + sens * rng.randint(85, 100)
            plat = barre(x, y, larg)
            # une etagere sur deux coulisse horizontalement (jamais deux de
            # suite) : il faut viser un rebond sur une cible en mouvement
            if not mobile_precedente and rng.random() < 0.62:
                course = rng.randint(40, 58)
                plat.vx = rng.choice((-1, 1)) * (2.0 + rng.random() * 1.0)
                plat.xmin = max(larg / 2 + 10, x - course)
                plat.xmax = min(W - larg / 2 - 10, x + course)
                mobile_precedente = True
            else:
                mobile_precedente = False
            plats.append(plat)
            if rng.random() < 0.5:                                 # un sac pose dessus
                croq = module_niveau._image("catfood", x, y_bas=y + 9)
                if croq is not None:
                    self.croquettes.append(croq)

        y += 95                                                     # le sommet, a portee
        sx = W / 2 + (rng.randint(-40, 40))
        plats.append(barre(sx, y, 320, 22, (120, 86, 56)))
        self.distributeur = module_niveau._image("distributeur", sx, y_bas=y + 11)
        self.monde_haut = y + 220

        # la tour devient la geometrie ; pas de murs (defilement + rebouclage)
        self.niveau.plateformes = plats
        self.niveau.murs = arcade.SpriteList()

        self.chat.center_x = W / 2
        self.chat.bottom = self.doodle_base_y      # pose sur le sol, pas dedans
        self.chat.change_x = 0.0
        self.chat.change_y = C.REBOND_DOODLE       # premier rebond immediat
        self.camera_y = 0.0
        self.camera_doodle = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        # le fond cuisine, toile de fond fixe du Doodle Jump
        self.fond_doodle = None
        chemin_fond = C.DOSSIER_IMAGES / "fonds" / "cuisine_doodle.png"
        if chemin_fond.is_file():
            self.fond_doodle = arcade.load_texture(chemin_fond)

    def on_show_view(self) -> None:
        self.window.background_color = C.COULEUR_FOND

    # ------------------------------------------------------------------
    def on_update(self, delta_time: float) -> None:
        if self.transition > 0:
            self.transition -= delta_time
            self.ambiance.mettre_a_jour(delta_time)
            return

        self.minuteur_message = max(0.0, self.minuteur_message - delta_time)

        # TODO (vies.py) : cette pause et l'enchainement des niveaux
        # appartiennent au systeme de vies. Ici, juste de quoi voir l'animation.
        if self.ralenti > 0:
            self.ralenti -= delta_time
            delta_time *= 0.35                # tout ralentit, l'instant de la mort
        self.flash = max(0.0, self.flash - delta_time * 2.2)

        if self.pause_mort > 0:
            self.pause_mort -= delta_time
            self.chat.center_y += 2.2         # le chat-ange s'envole
            self.chat.alpha = max(0, int(255 * min(1, self.pause_mort / 1.2)))
            self.chat.mettre_a_jour_animation(delta_time)
            self.effets.mettre_a_jour(delta_time)
            self.ambiance.mettre_a_jour(delta_time)
            if self.pause_mort <= 0:
                if getattr(self, "rejouer", False):
                    self.charger_niveau(self.numero_niveau)
                else:
                    self.niveau_suivant()
                self.chat.vivant = True
                self.chat.ange = False
                self.chat.alpha = 255
            return

        if self.doodle:
            self._update_doodle(delta_time)
            return

        au_sol = self.collisions.est_au_sol()
        self.chat.calculer_deplacement(delta_time, au_sol)
        contacts = self.collisions.mettre_a_jour(descendre=self.chat.veut_descendre)

        self._surfaces_glissantes(contacts)
        self._remplir_la_gamelle()
        if self.medecin is not None:
            self._somniferes_sur_le_medecin()
        self._sortir_du_sac()
        self._vivre_les_faux_pieges(delta_time)
        self._oter_le_deguisement(delta_time)
        if self.medecin is not None:
            self.medecin.mettre_a_jour(delta_time)
        self.effets.mettre_a_jour(delta_time)
        self.ambiance.mettre_a_jour(delta_time)      # la maison respire, en continu
        if self.camera_active:
            self.champ_x += (self.chat.center_x - self.champ_x) * 0.022
            self.champ_y += (self.chat.center_y - self.champ_y) * 0.022
        self._vivre_la_horde(delta_time)
        self._vivre_les_flammes(delta_time)
        self._vivre_les_piments(delta_time)
        self._vivre_les_croquettes(delta_time)
        if self.chat_noir is not None:
            self.chat_noir.mettre_a_jour(delta_time)
        if self.fille is not None and self.fille.mettre_a_jour(delta_time, self.chat):
            self.effets.pouf(self.chat.center_x, self.chat.center_y, (255, 120, 190), 22)
            self.effets.trembler(16)               # ca cogne : l ecran tremble
            self.audio.jouer("piege", 0.6)
            self.minuteur_deguisement = 4.0
        for pousseur in self.pousseurs:
            if pousseur.mettre_a_jour(delta_time, self.chat):
                self.effets.pouf(self.chat.center_x, self.chat.center_y, (200, 210, 235), 8)
                self.effets.trembler(4)
                self.audio.jouer("piege", 0.4)

        if contacts.atterrissage:
            self.chat.signaler_atterrissage()
            self.audio.jouer("atterrissage", 0.4)
        if contacts.esquive:
            self.afficher("Les moustaches ont senti le danger !")

        if not contacts.vivant:
            self.griller_une_vie(contacts.mort)

        if self.sortie is not None and arcade.check_for_collision(self.chat, self.sortie):
            self.gagner()

        if self.toupie > 0:
            self.toupie -= delta_time
            # il tourne vite puis ralentit, et se stabilise droit
            self.chat.angle = (self.toupie * 900) % 360 if self.toupie > 0.15 else 0
        self.chat.mettre_a_jour_animation(delta_time)

    def _update_doodle(self, delta_time: float) -> None:
        """Physique maison du Doodle Jump : rebond auto, rebouclage, camera qui monte."""
        pas = min(2.0, delta_time * 60.0)     # cale sur le pas de 60 ips du reste du jeu

        # 1. pilotage gauche/droite (le joueur ne fait que diriger)
        cible = 0.0
        if self.chat.veut_gauche:
            cible -= C.VITESSE_CHAT
        if self.chat.veut_droite:
            cible += C.VITESSE_CHAT
        self.chat.change_x += (cible - self.chat.change_x) * 0.30
        self.chat.center_x += self.chat.change_x * pas
        # rebouclage horizontal facon Doodle Jump
        if self.chat.center_x < 0:
            self.chat.center_x += C.LARGEUR_FENETRE
        elif self.chat.center_x > C.LARGEUR_FENETRE:
            self.chat.center_x -= C.LARGEUR_FENETRE

        # 1bis. les etageres coulissantes vont et viennent horizontalement
        for plat in self.niveau.plateformes:
            if plat.vx:
                plat.center_x += plat.vx * pas
                if plat.center_x < plat.xmin or plat.center_x > plat.xmax:
                    plat.vx = -plat.vx
                    plat.center_x = max(plat.xmin, min(plat.xmax, plat.center_x))

        # 2. gravite + rebond automatique quand on retombe sur une etagere
        self.chat.change_y = max(-C.VITESSE_CHUTE_MAX, self.chat.change_y - C.GRAVITE * pas)
        bas_avant = self.chat.bottom
        self.chat.center_y += self.chat.change_y * pas
        self.chat.au_sol = False
        if self.chat.change_y <= 0:
            for plat in self.niveau.plateformes:
                if (plat.left - 8 <= self.chat.center_x <= plat.right + 8
                        and self.chat.bottom <= plat.top <= bas_avant + 2):
                    self.chat.bottom = plat.top
                    self.chat.change_y = C.REBOND_DOODLE
                    self.chat.au_sol = True
                    self.effets.pouf(self.chat.center_x, plat.top, (210, 180, 120), 5)
                    self.audio.jouer("saut", 0.2)
                    break

        # 3. la camera suit le chat vers le haut, sans jamais redescendre
        self.camera_y = max(self.camera_y, self.chat.center_y - C.HAUTEUR_FENETRE * 0.42)
        # chute ratee : on repart du bas (sans perdre de vie)
        if self.chat.center_y < self.camera_y - 60:
            self._respawn_doodle()

        # 4. croquettes gobees + gavage au distributeur (remplit la satiete)
        self._vivre_les_croquettes(delta_time)

        self.chat.mettre_a_jour_animation(delta_time)
        self.effets.mettre_a_jour(delta_time)
        self.ambiance.mettre_a_jour(delta_time)

    def _respawn_doodle(self) -> None:
        """Le chat a rate un rebond : on le remet en bas de la tour."""
        self.chat.center_x = C.LARGEUR_FENETRE / 2
        self.chat.bottom = self.doodle_base_y
        self.chat.change_x = 0.0
        self.chat.change_y = C.REBOND_DOODLE
        self.camera_y = 0.0
        self.afficher("Rate ! On repart du bas.")

    def _dans_le_champ(self) -> bool:
        """Le chat est-il dans le champ de la camera de l'influenceur ?"""
        dx = self.chat.center_x - self.champ_x
        dy = self.chat.center_y - self.champ_y
        return (dx * dx + dy * dy) ** 0.5 <= self.champ_rayon

    def _action_possible(self) -> bool:
        """Y a-t-il quelque chose a faire avec E, la, maintenant ?"""
        if self.chat.dans_le_sac or not self.chat.vivant:
            return False
        for zone in self.faux_pieges:
            if (zone.effet["declenchement"] == "action" and zone.recharge <= 0
                    and arcade.check_for_collision(self.chat, zone)):
                return True
        if self.gamelle is not None and arcade.check_for_collision(self.chat, self.gamelle):
            if getattr(self.niveau, "piege_direct", False) or self.gamelle.remplie:
                return True
        if self.chat_noir is not None and arcade.check_for_collision(self.chat, self.chat_noir):
            return True
        depart = self.chat.center_x
        self.chat.center_x += self.chat.regarde * PORTEE_ACTION
        pres_du_sac = bool(arcade.check_for_collision_with_list(self.chat, self.niveau.poussables))
        self.chat.center_x = depart
        return pres_du_sac

    def _libelle_action(self) -> str:
        """Le nom de ce que le chat peut faire ici (affiche au-dessus de lui)."""
        if self.chat_noir is not None and arcade.check_for_collision(self.chat, self.chat_noir):
            return "Le chat noir"
        for zone in self.faux_pieges:
            if (zone.effet["declenchement"] == "action" and zone.recharge <= 0
                    and arcade.check_for_collision(self.chat, zone)):
                return LIBELLES.get(zone.effet.get("image", ""), "Essayer")
        if self.gamelle is not None and arcade.check_for_collision(self.chat, self.gamelle):
            return (getattr(self.niveau, "libelle_piege", "")
                    or LIBELLES.get(self.niveau.piege_image, "Le piege"))
        return "Le sac de croquettes"

    def _draw_doodle(self) -> None:
        """Rendu du Doodle Jump : la cuisine fixe en fond, la tour sous la camera."""
        W, H = C.LARGEUR_FENETRE, C.HAUTEUR_FENETRE
        # la cuisine sert de toile de fond fixe, ajustee a la fenetre
        fond = self.fond_doodle if getattr(self, "fond_doodle", None) is not None \
            else (self.fond.texture if self.fond is not None else None)
        if fond is not None:
            arcade.draw_texture_rect(fond, arcade.LBWH(0, 0, W, H), pixelated=True)
        # le monde qui defile, vu par la camera verticale
        self.camera_doodle.position = (W / 2, self.camera_y + H / 2)
        self.camera_doodle.use()
        self.niveau.plateformes.draw(pixelated=True)
        self.croquettes.draw(pixelated=True)
        if self.distributeur is not None:
            arcade.draw_sprite(self.distributeur, pixelated=True)
        arcade.draw_sprite(self.chat, pixelated=True)
        self.effets.dessiner()
        # le HUD, repere fixe a l ecran
        self.gui_camera.use()
        self._dessiner_barre_satiete()
        arcade.draw_text("Dirige gauche / droite (Q D ou fleches) - le chat rebondit tout seul",
                         W / 2, 18, C.COULEUR_TEXTE, 14, anchor_x="center")
        if self.minuteur_message > 0 and self.message:
            arcade.draw_text(self.message, W / 2, H * 0.5, (255, 240, 220), 22,
                             anchor_x="center", bold=True)
        if self.transition > 0:
            self._dessiner_transition()

    def _dessiner_barre_satiete(self) -> None:
        """La barre de satiete a REMPLIR (niveau 1) : pleine = le ventre lache."""
        L = C.LARGEUR_FENETRE
        x, y, larg, haut = L/2 - 200, C.HAUTEUR_FENETRE - 60, 400, 22
        arcade.draw_lrbt_rectangle_filled(x, x+larg, y, y+haut, (24, 20, 30))
        ratio = self.satiete / C.SATIETE_MAX
        couleur = (150, 96, 50) if ratio < 0.7 else (210, 90, 60)
        arcade.draw_lrbt_rectangle_filled(x, x + larg*ratio, y, y+haut, couleur)
        arcade.draw_lrbt_rectangle_outline(x, x+larg, y, y+haut, (240, 230, 220), 2)
        arcade.draw_text("Escalade jusqu au distributeur et gave-toi de croquettes !",
                         L/2, y + haut + 8, (255, 240, 220), 15, anchor_x="center", bold=True)
        arcade.draw_text(f"{int(self.satiete)} %", L/2, y+4, (255,255,255), 13, anchor_x="center", bold=True)

    def _dessiner_barre_vie(self) -> None:
        """La barre de vie a vider (niveau 5) : plus elle est basse, mieux c'est."""
        L = C.LARGEUR_FENETRE
        x, y, larg, haut = L/2 - 200, C.HAUTEUR_FENETRE - 60, 400, 22
        arcade.draw_lrbt_rectangle_filled(x, x+larg, y, y+haut, (30, 20, 24))
        ratio = self.vie_barre / C.VIE_MAX
        couleur = (200, 60, 50) if ratio > 0.3 else (240, 180, 60)
        arcade.draw_lrbt_rectangle_filled(x, x + larg*ratio, y, y+haut, couleur)
        arcade.draw_lrbt_rectangle_outline(x, x+larg, y, y+haut, (240, 230, 220), 2)
        arcade.draw_text("Mange les piments : vide ta barre de vie !",
                         L/2, y + haut + 8, (255, 240, 220), 15, anchor_x="center", bold=True)
        arcade.draw_text(f"{int(self.vie_barre)}", L/2, y+4, (255,255,255), 13, anchor_x="center", bold=True)

    def _dessiner_transition(self) -> None:
        """L'ecran de lore : la nouvelle famille et son probleme."""
        L, H = C.LARGEUR_FENETRE, C.HAUTEUR_FENETRE
        fondu = min(1.0, self.transition, 5.0 - self.transition + 1)
        arcade.draw_lrbt_rectangle_filled(0, L, 0, H, (16, 14, 22, int(240 * min(1, self.transition))))
        cx = L / 2
        arcade.draw_text(f"Vie {self.numero_niveau} sur {C.NOMBRE_NIVEAUX}",
                         cx, H * 0.70, (150, 150, 165), 18, anchor_x="center")
        arcade.draw_text("Nouvelle famille", cx, H * 0.60, (200, 180, 120), 22,
                         anchor_x="center", bold=True)
        arcade.draw_text(self.niveau.famille, cx, H * 0.52, (255, 250, 235), 34,
                         anchor_x="center", bold=True)
        arcade.draw_text("Probleme", cx, H * 0.38, (210, 120, 120), 22,
                         anchor_x="center", bold=True)
        arcade.draw_text(self.niveau.probleme, cx, H * 0.30, (255, 220, 220), 26,
                         anchor_x="center", width=int(L * 0.8), align="center", multiline=True)
        if self.transition < 4.2:
            arcade.draw_text("Espace / Entree pour continuer", cx, H * 0.12,
                             (150, 150, 165), 15, anchor_x="center")

    def _dessiner_indicateur_action(self) -> None:
        """Un E au-dessus du chat, avec le nom de l'action, quand E fera qqch."""
        if not self._action_possible():
            return
        x = self.chat.center_x
        y = self.chat.top + 16
        libelle = self._libelle_action()

        # le petit E dans son cadre
        arcade.draw_lrbt_rectangle_filled(x - 11, x + 11, y - 3, y + 19, (20, 18, 26))
        arcade.draw_lrbt_rectangle_outline(x - 11, x + 11, y - 3, y + 19, (240, 220, 120), 2)
        arcade.draw_text("E", x, y, (240, 220, 120), 14, anchor_x="center", bold=True)
        # le nom de l'item, juste au-dessus, avec un contour au lieu d'un fond
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            arcade.draw_text(libelle, x + dx, y + 26 + dy, (20, 18, 26), 12, anchor_x="center", bold=True)
        arcade.draw_text(libelle, x, y + 26, (255, 240, 190), 12, anchor_x="center", bold=True)

    # ------------------------------------------------------------------
    # Les faux pieges scriptes
    # ------------------------------------------------------------------
    def _construire_faux_pieges(self) -> None:
        """Transforme les lettres de la carte en zones qui reagissent au chat.

        Chaque niveau declare ses faux pieges dans game/les_niveaux.py :
        une lettre sur la carte, et un effet. Regle n.1 du jeu : tout ce qui a
        l'air mortel doit rater. C'est ici que ca rate.
        """
        self.faux_pieges = arcade.SpriteList()
        self.images_pieges = arcade.SpriteList()
        for lettre, effet in self.niveau.faux_pieges.items():
            x, y = self.niveau.point(effet["pos"])
            largeur = int(C.TAILLE_TUILE * effet.get("largeur", 1.4))
            hauteur = int(C.TAILLE_TUILE * effet.get("hauteur", 1.2))
            zone = arcade.Sprite(
                arcade.Texture.create_empty(f"fp_{lettre}", (largeur, hauteur)),
                center_x=x, center_y=y + hauteur / 2,
            )
            zone.effet = dict(effet)
            zone.effet.setdefault("declenchement", "action")
            zone.recharge = 0.0
            self.faux_pieges.append(zone)

            # un piege invisible n'existe pas : chaque zone montre son image
            image = module_niveau._image(effet.get("image", ""), x, y_bas=y)
            if image is not None:
                self.images_pieges.append(image)

    def _vivre_les_faux_pieges(self, delta_time: float) -> None:
        """Les pieges au contact se declenchent tout seuls, puis se rearment."""
        for zone in self.faux_pieges:
            zone.recharge = max(0.0, zone.recharge - delta_time)
            if (zone.effet["declenchement"] == "contact" and zone.recharge <= 0
                    and arcade.check_for_collision(self.chat, zone)):
                self._declencher(zone)

    def _declencher(self, zone) -> None:
        """Applique l'effet d'un faux piege. Aucun ne tue : c'est le principe."""
        effet, chat = zone.effet, self.chat
        zone.recharge = effet.get("recharge", 2.5)

        genre = effet.get("effet", "message")

        # le medecin dort ? alors ses methodes de soin sont devenues des fins.
        if (genre == "soin" and self.niveau.docteur
                and self.gamelle is not None and self.gamelle.remplie):
            self.griller_une_vie(effet.get("cause", "le cabinet"))
            return

        if "texte" in effet:
            self.afficher(effet["texte"])
        self.effets.pouf(chat.center_x, chat.top, (230, 235, 255), 10)
        self.effets.trembler(5)
        self.audio.jouer("piege", 0.5)
        if effet.get("effet") not in ("projection",):
            chat.change_y = 7                 # un petit sursaut de surprise
        if genre == "projection":
            # lance en l'air facon poupee, pousse par un autre chat...
            chat.change_x, chat.change_y = effet.get("vitesse", (0, 16))
            chat.minuteur_sac = 0.0
        elif genre == "soin":
            # le medecin le soigne, le maitre le rattrape : retour case depart
            if self.medecin is not None:
                self.medecin.soigner(chat.center_x)
            chat.replacer_au_depart()
        elif genre == "deguisement":
            # maquille facon poupee : humiliant, pas dangereux
            chat.color = effet.get("teinte", (255, 150, 200))
            self.minuteur_deguisement = effet.get("duree", 4.0)
        elif genre == "sac":
            chat.coincer_dans_le_sac()
        elif genre == "endort":
            # les somniferes : le chat les renverse sur le medecin, il s'endort
            if self.medecin is not None and not self.medecin.endormi and self.gamelle is not None:
                self.medecin.endormir()
                self.gamelle.remplie = True
        elif genre == "toupie":
            # manque de tomber en tournant sur lui-meme, puis se rattrape
            self.toupie = effet.get("duree", 1.1)

    def _oter_le_deguisement(self, delta_time: float) -> None:
        if getattr(self, "minuteur_deguisement", 0) > 0:
            self.minuteur_deguisement -= delta_time
            if self.minuteur_deguisement <= 0:
                self.chat.color = (255, 255, 255)

    # ------------------------------------------------------------------
    # Le salon : verre glissant, gamelle, sac de croquettes
    # ------------------------------------------------------------------
    def _surfaces_glissantes(self, contacts) -> None:
        """La table du salon n'est pas en verre, c'est un film plastique."""
        self.chat.sur_surface_glissante = any(
            getattr(zone, "role", "") == "verre" for zone in contacts.zones
        )

    def _somniferes_sur_le_medecin(self) -> None:
        """Niveau 6 : des somniferes qui tombent sur le medecin l'endorment."""
        if (self.medecin is None or self.medecin.endormi or self.gamelle is None
                or self.gamelle.remplie):
            return
        touches = arcade.check_for_collision_with_list(self.medecin, self.niveau.poussables)
        if touches:
            self.gamelle.remplie = True
            self.medecin.endormir()
            for objet in touches:
                objet.remove_from_sprite_lists()
            self.afficher(self.niveau.message_piege
                          or "Les somniferes tombent sur le medecin. Il glisse. Il ronfle.")

    def _remplir_la_gamelle(self) -> None:
        """Un objet renverse dans la gamelle y deverse son contenu."""
        if self.gamelle is None or self.gamelle.remplie:
            return

        renverse = arcade.check_for_collision_with_list(
            self.gamelle, self.niveau.poussables
        )
        if renverse:
            self.gamelle.remplie = True
            self.gamelle.color = C.COULEUR_POUSSABLE
            # le sac se vide entierement dans la gamelle : on le retire, sinon
            # il resterait plante devant et empecherait le chat de manger
            for objet in renverse:
                objet.remove_from_sprite_lists()
            if self.medecin is not None:
                self.medecin.endormir()
            if getattr(self.niveau, "horde", False):
                self._lancer_la_horde()
            self.afficher(self.niveau.message_piege
                          or "Le sac se renverse dans la gamelle. Les croquettes du fond, celles qui sentent.")

    def _sortir_du_sac(self) -> None:
        """Le chat coince dans le sac s'arrete des qu'il percute quelque chose."""
        if self.chat.dans_le_sac and abs(self.chat.change_x) < 0.5:
            self.chat.liberer_du_sac()
            self.afficher("Le chat percute le mur. Il se degage. Toujours vivant.")

    def manger(self) -> None:
        """Le seul vrai danger du salon."""
        if self.gamelle is None:
            return
        if not arcade.check_for_collision(self.chat, self.gamelle):
            return

        if self.gamelle.remplie and self.niveau.docteur:
            self.afficher("Il dort profondement. A toi de choisir ta fin.")
        elif self.gamelle.remplie:
            self.griller_une_vie("les croquettes avariees")
        else:
            self.afficher(self.niveau.message_attente
                          or "Les memes croquettes que tous les soirs. Meme pas de quoi s etouffer.")

    def se_coincer_dans_le_sac(self) -> bool:
        """Faux piege : le chat met la tete dans le sac et fonce dans le decor.

        On regarde **devant** le chat : un objet solide ne le chevauche jamais,
        le moteur les a separes. Sans ce decalage, E ne marcherait jamais.
        """
        depart = self.chat.center_x
        self.chat.center_x += self.chat.regarde * PORTEE_ACTION
        touche = arcade.check_for_collision_with_list(self.chat, self.niveau.poussables)
        self.chat.center_x = depart

        if not touche:
            return False
        self.chat.coincer_dans_le_sac()
        self.afficher("Le chat a la tete dans le sac. Il ne voit plus rien.")
        return True

    def _flamme_active(self, f) -> bool:
        """Le jet de feu est allume ~1,2 s toutes les 2,4 s, decale par jet."""
        cycle = (self.ambiance.t + f["phase"]) % 2.4
        return cycle < 1.2

    def _hauteur_flamme(self, f) -> float:
        """La hauteur du jet quand il est allume (0 -> 70 px), pour l'animation."""
        cycle = (self.ambiance.t + f["phase"]) % 2.4
        if cycle >= 1.2:
            return 0.0
        montee = min(cycle, 0.25) / 0.25
        descente = min(max(1.2 - cycle, 0), 0.25) / 0.25
        return 70 * min(montee, descente) * (0.85 + 0.15 * math.sin(self.ambiance.t * 30))

    def _vivre_les_flammes(self, delta_time: float) -> None:
        """Un jet allume qui touche le chat le fait reculer (il ne le tue pas)."""
        for f in self.flammes:
            if not self._flamme_active(f):
                continue
            h = self._hauteur_flamme(f)
            if (abs(self.chat.center_x - f["x"]) < 34
                    and 0 < self.chat.bottom - f["y"] < h + 10):
                self.chat.change_x = 12 if self.chat.center_x > f["x"] else -12
                self.chat.change_y = 6

    def _dessiner_les_flammes(self) -> None:
        for f in self.flammes:
            h = self._hauteur_flamme(f)
            if h <= 0:
                continue
            import random
            for _ in range(int(h / 5)):
                py = f["y"] + random.random() * h
                t = (py - f["y"]) / h                 # 0 en bas, 1 en haut
                r = (18 - t * 12) * (0.6 + 0.4 * random.random())
                couleur = (255, int(220 - t * 140), int(60 - t * 50), int(220 * (1 - t)))
                arcade.draw_circle_filled(f["x"] + (random.random() - 0.5) * 16, py, r, couleur)

    def _lancer_la_horde(self) -> None:
        """La cloche a sonne : cent chats affames deferlent des deux cotes."""
        if self.horde_lancee:
            return
        self.horde_lancee = True
        sol = self.niveau.point("salon")[1]
        import random
        for i in range(40):
            cote = -1 if i % 2 == 0 else 1
            depart = -60 - random.random() * 500 if cote > 0 else self.niveau.largeur + 60 + random.random() * 500
            from game.entites import frames
            droite, gauche = frames("course")
            jeu = droite if cote > 0 else gauche
            chat = arcade.Sprite(jeu[i % len(jeu)], scale=2.4)
            chat.frames_horde = jeu
            chat.center_x = depart
            chat.bottom = sol + random.random() * 90
            chat.vx = (5 + random.random() * 4) * cote
            self.horde.append(chat)

    def _vivre_la_horde(self, delta_time: float) -> None:
        if not len(self.horde):
            return
        for chat in self.horde:
            chat.center_x += chat.vx
            chat.center_y += math.sin(self.ambiance.t * 20 + chat.center_x) * 1.5
            fr = chat.frames_horde
            chat.texture = fr[int(self.ambiance.t * 14 + chat.center_x) % len(fr)]
            if chat.center_x < -120 or chat.center_x > self.niveau.largeur + 120:
                chat.remove_from_sprite_lists()
        if self.chat.vivant and arcade.check_for_collision_with_list(self.chat, self.horde):
            self.griller_une_vie("cent chats affames")

    def _vivre_les_croquettes(self, delta_time: float) -> None:
        """Niveau 1 : ramasser les croquettes et se gaver au distributeur.

        La satiete monte a chaque croquette gobee et deborde vite au pied du
        distributeur ; a fond, le petit ventre lache et le chat change de vie.
        """
        if self.distributeur is None or not self.chat.vivant:
            return
        if C.SATIETE_DIGESTION:
            self.satiete = max(0.0, self.satiete - C.SATIETE_DIGESTION * delta_time)
        # les croquettes semees sur les etageres, gobees une seule fois
        for croq in self.croquettes:
            if croq.alpha == 255 and arcade.check_for_collision(self.chat, croq):
                self.satiete = min(C.SATIETE_MAX, self.satiete + C.CROQUETTE_GAVE)
                croq.alpha = 0
                self.effets.pouf(croq.center_x, croq.center_y, (200, 150, 90), 6)
                self.audio.jouer("atterrissage", 0.3)
        # le gros distributeur, tout en haut : il deverse tant qu on le touche
        if arcade.check_for_collision(self.chat, self.distributeur):
            self.satiete = min(C.SATIETE_MAX, self.satiete + C.DISTRIBUTEUR_GAVE * delta_time)
            if int(self.ambiance.t * 20) % 4 == 0:
                self.effets.pouf(self.chat.center_x, self.chat.center_y + 6, (200, 150, 90), 3)
        if self.satiete >= C.SATIETE_MAX:
            self.griller_une_vie("un ventre trop plein")

    def _vivre_les_piments(self, delta_time: float) -> None:
        """Niveau 5 : manger les piments vide la barre ; elle remonte toute seule."""
        if not len(self.piments) or not self.chat.vivant:
            return
        # la barre remonte petit a petit (c'est la difficulte)
        self.vie_barre = min(C.VIE_MAX, self.vie_barre + C.VIE_REGEN * delta_time)
        for piment in self.piments:
            if piment.alpha < 255:           # piment mange, en attente de repop
                piment.repop -= delta_time
                if piment.repop <= 0:
                    piment.alpha = 255
                continue
            if arcade.check_for_collision(self.chat, piment):
                self.vie_barre = max(0.0, self.vie_barre - C.PIMENT_DEGATS)
                piment.alpha = 60
                piment.repop = C.PIMENT_RESPAWN
                self.effets.pouf(piment.center_x, piment.center_y, (240, 80, 60), 8)
                self.audio.jouer("piege", 0.4)
                if self.vie_barre <= 0:
                    self.griller_une_vie("trop de piments")
                return

    def griller_une_vie(self, cause: str) -> None:
        """Le chat change de vie.

        Dans les six premiers niveaux, c'est l'objectif : la vie brulee fait
        passer au foyer suivant. Au septieme, le jeu s'inverse — le chat est
        enfin heureux, mourir devient l'echec et on recommence le niveau.
        """
        if self.termine:
            return

        self.chat.vivant = False
        self.chat.ange = True                 # il s'envole en chat-ange
        self.chat.change_x = self.chat.change_y = 0
        self.pause_mort = 1.8
        self.ralenti = 0.5
        self.flash = 1.0
        self.effets.pouf(self.chat.center_x, self.chat.center_y, (255, 224, 120), 26)
        self.effets.trembler(13)
        self.audio.jouer("mort")

        if self.niveau.survivre:
            self.afficher(self.niveau.message_mort
                          or f"Pas comme ca. Pas maintenant. ({cause})")
            self.rejouer = True
            return

        self.vies -= 1
        self.rejouer = False
        self.afficher(self.niveau.message_mort
                      or f"Une vie de moins, emportee par {cause}. Il en reste {self.vies}.")

    def gagner(self) -> None:
        """Dernier niveau : le chat a tenu. C'est fini."""
        if self.termine:
            return
        self.termine = True
        self.audio.jouer("win")
        self.afficher("Il est reste. Pour une fois, il est reste.")

    def niveau_suivant(self) -> None:
        if self.numero_niveau >= C.NOMBRE_NIVEAUX:
            self.termine = True
            self.afficher("Sept vies, sept maisons. Il ne lui en restait qu'une.")
            return
        self.charger_niveau(self.numero_niveau + 1)

    def afficher(self, texte: str) -> None:
        self.message = texte
        self.minuteur_message = 4.0

    # ------------------------------------------------------------------
    def on_draw(self) -> None:
        self.clear()
        if self.doodle:
            self._draw_doodle()
            return
        dx, dy = self.effets.decalage()
        if self.fond is not None:
            self.fond.center_x += dx
            self.fond.center_y += dy
            arcade.draw_sprite(self.fond, pixelated=True)
            self.fond.center_x -= dx
            self.fond.center_y -= dy
        self.ambiance.dessiner()
        self.niveau.dessiner()
        self.images_pieges.draw(pixelated=True)
        self.pousseurs.draw(pixelated=True)
        self.horde.draw(pixelated=True)
        self._dessiner_les_flammes()
        if self.distributeur is not None:
            arcade.draw_sprite(self.distributeur, pixelated=True)
        self.croquettes.draw(pixelated=True)
        self.piments.draw(pixelated=True)
        if self.piege_frames and self.gamelle is not None:
            fr = self.piege_frames[int(self.ambiance.t * 12) % len(self.piege_frames)]
            ech = min(120 / fr.width, 90 / fr.height)
            arcade.draw_texture_rect(
                fr, arcade.LBWH(self.gamelle.center_x - fr.width*ech/2,
                                self.gamelle.center_y - fr.height*ech/2,
                                fr.width*ech, fr.height*ech), pixelated=True)
        if self.chat_noir is not None:
            arcade.draw_sprite(self.chat_noir, pixelated=True)
        if self.fille is not None:
            arcade.draw_sprite(self.fille, pixelated=True)
        if self.medecin is not None:
            arcade.draw_sprite(self.medecin, pixelated=True)
            if self.medecin.endormi:
                arcade.draw_text("Zzz", self.medecin.center_x + 30,
                                 self.medecin.top + 6, (240, 220, 120), 16, bold=True)
        arcade.draw_sprite(self.chat, pixelated=True)
        if self.camera_active:
            dedans = self._dans_le_champ()
            # couleurs inversees : rouge quand le chat est DANS le champ, vert
            # quand il est en DEHORS
            couleur = (240, 120, 120, 40) if dedans else (120, 240, 160, 30)
            arcade.draw_circle_filled(self.champ_x, self.champ_y, self.champ_rayon, couleur)
            arcade.draw_circle_outline(self.champ_x, self.champ_y, self.champ_rayon,
                                       (255, 150, 150) if dedans else (150, 255, 190), 3)
        self.effets.dessiner()
        if self.flash > 0:
            arcade.draw_lrbt_rectangle_filled(
                0, C.LARGEUR_FENETRE, 0, C.HAUTEUR_FENETRE,
                (255, 255, 255, int(200 * self.flash)))
        self._dessiner_indicateur_action()

        if self.debug:
            self.collisions.dessiner_debug()

        arcade.draw_text(
            f"{self.numero_niveau}/{C.NOMBRE_NIVEAUX}  {self.niveau.titre}     Vies : {self.vies}",
            16, C.HAUTEUR_FENETRE - 30, C.COULEUR_TEXTE, 16,
        )
        if self.niveau.aide:
            arcade.draw_text(
                self.niveau.aide, C.LARGEUR_FENETRE / 2, 16,
                C.COULEUR_TEXTE_FADE, 13, anchor_x="center",
            )
        # Plus de message flottant au-dessus du chat : le seul texte affiche
        # au-dessus de lui est l'indicateur d'action (le E), et seulement quand
        # une action est possible (voir _dessiner_indicateur_action).

        if len(self.piments):
            self._dessiner_barre_vie()
        if self.distributeur is not None:
            self._dessiner_barre_satiete()

        if self.transition > 0:
            self._dessiner_transition()

    # ------------------------------------------------------------------
    def on_key_press(self, touche: int, modificateurs: int) -> None:
        if self.transition > 0:
            if touche in (arcade.key.SPACE, arcade.key.ENTER, arcade.key.RETURN):
                self.transition = 0.0
            return

        if touche in C.TOUCHES_GAUCHE:
            self.chat.veut_gauche = True
        elif touche in C.TOUCHES_DROITE:
            self.chat.veut_droite = True
        elif touche in C.TOUCHES_BAS:
            self.chat.veut_descendre = True

        if self.doodle:                       # en doodle : pas de saut ni de descente manuels
            return

        if touche in C.TOUCHES_SAUT:
            if self.chat.au_sol:
                self.audio.jouer("saut", 0.5)
            self.chat.demander_saut()
        elif touche in C.TOUCHES_ACTION:
            self.interagir()
        elif touche in C.TOUCHES_RECOMMENCER:
            self.charger_niveau(self.numero_niveau)
        elif touche in C.TOUCHES_DEBUG:
            self.debug = not self.debug
        elif touche in C.TOUCHES_PAUSE:
            arcade.exit()

    def interagir(self) -> None:
        """Touche E : le chat essaie quelque chose la ou il est.

        La gamelle passe avant le sac : une fois les croquettes renversees, le
        sac vide traine juste a cote, et ce serait rageant de rater le repas.
        """
        if self.chat.dans_le_sac:
            return
        if self.chat_noir is not None and arcade.check_for_collision(self.chat, self.chat_noir):
            self.griller_une_vie(self.niveau.message_mort or "emporte par le chat noir")
            return
        if self.gamelle is not None and arcade.check_for_collision(self.chat, self.gamelle):
            if getattr(self.niveau, "piege_direct", False):
                if self.camera_active and self._dans_le_champ():
                    self.afficher("L influenceur te filme ! Il te tire du cable pour la video.")
                    return
                self.griller_une_vie(self.niveau.message_mort or "le piege")
                return
            if self.gamelle.remplie:
                self.manger()
                return
        for zone in self.faux_pieges:
            if (zone.effet["declenchement"] == "action" and zone.recharge <= 0
                    and arcade.check_for_collision(self.chat, zone)):
                self._declencher(zone)
                return
        if self.se_coincer_dans_le_sac():
            return
        self.manger()

    def on_key_release(self, touche: int, modificateurs: int) -> None:
        if touche in C.TOUCHES_GAUCHE:
            self.chat.veut_gauche = False
        elif touche in C.TOUCHES_DROITE:
            self.chat.veut_droite = False
        elif touche in C.TOUCHES_BAS:
            self.chat.veut_descendre = False

        if touche in C.TOUCHES_SAUT:
            self.chat.relacher_saut()

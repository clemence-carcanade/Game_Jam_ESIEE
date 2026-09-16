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
        self._construire_faux_pieges()

        # la fille (niveau 3) : elle poursuit et rejette le chat
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

    def on_show_view(self) -> None:
        self.window.background_color = C.COULEUR_FOND

    # ------------------------------------------------------------------
    def on_update(self, delta_time: float) -> None:
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

        au_sol = self.collisions.est_au_sol()
        self.chat.calculer_deplacement(delta_time, au_sol)
        contacts = self.collisions.mettre_a_jour(descendre=self.chat.veut_descendre)

        self._surfaces_glissantes(contacts)
        self._remplir_la_gamelle()
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
        if self.chat_noir is not None:
            self.chat_noir.mettre_a_jour(delta_time)
        if self.fille is not None and self.fille.mettre_a_jour(delta_time, self.chat):
            self.afficher("Elle t attrape, te maquille et te balance a l autre bout.")
            self.effets.pouf(self.chat.center_x, self.chat.top, (255, 180, 210), 10)
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
            return LIBELLES.get(self.niveau.piege_image, "Le piege")
        return "Le sac de croquettes"

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
        # le nom de l'item, juste au-dessus
        larg = 8 + len(libelle) * 7
        arcade.draw_lrbt_rectangle_filled(x - larg/2, x + larg/2, y + 22, y + 42, (20, 18, 26, 220))
        arcade.draw_text(libelle, x, y + 26, (250, 240, 200), 12, anchor_x="center", bold=True)

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
        self.minuteur_message = 2.5

    # ------------------------------------------------------------------
    def on_draw(self) -> None:
        self.clear()
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
            couleur = (120, 240, 160, 40) if dedans else (240, 120, 120, 30)
            arcade.draw_circle_filled(self.champ_x, self.champ_y, self.champ_rayon, couleur)
            arcade.draw_circle_outline(self.champ_x, self.champ_y, self.champ_rayon,
                                       (150, 255, 190) if dedans else (255, 150, 150), 3)
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
        if self.minuteur_message > 0 and self.chat is not None:
            # au-dessus du chat, en petit, avec un fond pour rester lisible
            x = min(max(self.chat.center_x, 220), C.LARGEUR_FENETRE - 220)
            y = self.chat.top + 48
            larg = 12 + len(self.message) * 6.5
            a = int(230 * min(1, self.minuteur_message))
            arcade.draw_lrbt_rectangle_filled(x - larg/2, x + larg/2, y - 4, y + 20, (20, 18, 26, a))
            arcade.draw_text(self.message, x, y, (250, 245, 230, 255), 12,
                             anchor_x="center", width=int(larg), align="center")

    # ------------------------------------------------------------------
    def on_key_press(self, touche: int, modificateurs: int) -> None:
        if touche in C.TOUCHES_GAUCHE:
            self.chat.veut_gauche = True
        elif touche in C.TOUCHES_DROITE:
            self.chat.veut_droite = True
        elif touche in C.TOUCHES_BAS:
            self.chat.veut_descendre = True

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

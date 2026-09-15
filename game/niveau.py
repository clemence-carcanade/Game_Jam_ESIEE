"""Lecture d'un niveau depuis ``niveaux/niveau_N.txt``.

Format du fichier (c'est le contrat qui permet à tout le monde de créer du
contenu sans toucher au code) :

* **1re ligne** : les métadonnées, en JSON, sur une seule ligne.

      {"titre": "Chez Léo", "maitre": "leo", "aide": "Les poufs amortissent tout."}

* **lignes suivantes** : la carte, un caractère = une tuile de 64 x 64.
  La première ligne de carte est le **haut** du niveau (on dessine comme on
  lit). L'origine (0, 0) d'arcade reste en bas à gauche.

      .   vide                    O   objet poussable (sac, caisse, pouf)
      #   mur / sol               B   bouton / plaque de pression
      =   plateforme traversable  D   porte (s'ouvre avec le bouton)
      C   départ du chat          1-9 mobilier (voir MOBILIER plus bas)
      M   départ du maître        X   élément mortel

Le mobilier (1 à 9) est décrit dans le dictionnaire ``MOBILIER`` : un nom, une
hauteur en fraction de tuile, une couleur et un comportement. Les couleurs sont
des **placeholders** : quand les tuiles des packs arriveront, il suffira de
remplacer la couleur par une image, le reste du code ne bouge pas.

Les métadonnées acceptent aussi les réflexes à désactiver au chargement :

      {"titre": "...", "reflexes_coupes": ["moustaches"]}
"""

import json
from dataclasses import dataclass, field

import arcade

from game import constantes as C


#: les images du décor sont dessinées en 32 px et affichées x2, comme le chat
ECHELLE_DECOR = C.TAILLE_TUILE / 32
DOSSIER_DECOR = C.DOSSIER_IMAGES / "decor"

_textures = {}


def _carre(largeur, hauteur, couleur, x, y, nom):
    """Un rectangle plein : sert de secours quand l'image n'existe pas encore,
    et de forme de collision invisible (couleur transparente)."""
    texture = arcade.Texture.create_empty(nom, (int(largeur), int(hauteur)), couleur)
    return arcade.Sprite(texture, center_x=x, center_y=y)


def _texture(nom):
    """Charge ``assets/images/decor/<nom>.png``, ou None si elle n'existe pas."""
    if nom not in _textures:
        chemin = DOSSIER_DECOR / f"{nom}.png"
        _textures[nom] = arcade.load_texture(chemin) if chemin.is_file() else None
    return _textures[nom]


def _image(nom, x, y_bas=None, y_haut=None):
    """Pose une image de décor. None si elle n'existe pas encore.

    On calcule le centre à partir de la hauteur de l'image, **jamais** avec
    ``sprite.bottom`` : arcade aligne alors la boîte de collision, qui ignore
    les pixels transparents. Une image à moitié vide se retrouverait décalée.
    """
    texture = _texture(nom)
    if texture is None:
        return None

    hauteur = texture.height * ECHELLE_DECOR
    sprite = arcade.Sprite(texture, scale=ECHELLE_DECOR, center_x=x)
    if y_haut is not None:
        sprite.center_y = y_haut - hauteur / 2
    else:
        sprite.center_y = y_bas + hauteur / 2
    sprite.nom = nom
    return sprite


def _nom_du_mur(carte, ligne, colonne):
    """Sol, plafond ou mur ? On regarde ce qu'il y a au-dessus et en dessous.

    Une case pleine dont le dessus est vide, c'est du sol : c'est là qu'on
    marche. Une case pleine dont le dessous est vide, c'est le plafond.
    """
    if carte is None:
        return "mur"

    def case(l, c):
        if 0 <= l < len(carte) and 0 <= c < len(carte[l]):
            return carte[l][c]
        return C.CAR_MUR

    if case(ligne - 1, colonne) != C.CAR_MUR:
        return "sol"
    if case(ligne + 1, colonne) != C.CAR_MUR:
        return "plafond"
    return "mur"


def _morceau(nom, carte, ligne, colonne):
    """Choisit le morceau gauche / milieu / droite d'un meuble selon ses voisins.

    Un canapé de trois cases s'écrit ``333`` : la première prend ``canape_g``,
    la deuxième ``canape_m``, la troisième ``canape_d``. Rien à faire de plus
    dans le fichier de niveau.
    """
    def case(l, c):
        if 0 <= l < len(carte) and 0 <= c < len(carte[l]):
            return carte[l][c]
        return None

    ici = carte[ligne][colonne]

    # meubles sur plusieurs rangées : etagere_haut_* / etagere_bas_*
    if _texture(f"{nom}_haut_m") is not None:
        rangee = "bas" if case(ligne - 1, colonne) == ici else "haut"
        nom = f"{nom}_{rangee}"

    if _texture(f"{nom}_m") is None:
        return nom

    gauche = case(ligne, colonne - 1) == ici
    droite = case(ligne, colonne + 1) == ici
    if gauche and droite:
        return f"{nom}_m"
    if droite:
        return f"{nom}_g"
    if gauche:
        return f"{nom}_d"
    return f"{nom}_m"


#: mobilier du jeu : caractère -> (nom, hauteur en tuiles, couleur, comportement)
#:
#: Comportements possibles :
#:   "decor"      dessiné, mais on le traverse (télé, plante, tapis, habitants)
#:   "plateforme" traversable par le bas, on peut se poser dessus (canapé)
#:   "mur"        solide de tous les côtés (buffet)
#:   "verre"      plateforme + surface glissante (la table du salon)
#:   "gamelle"    zone : c'est là que le chat peut manger
MOBILIER = {
    "1": ("gamelle_vide", 0.45, C.COULEUR_GAMELLE, "gamelle"),
    "2": ("table_verre", 0.25, C.COULEUR_VERRE, "verre"),
    "3": ("canape", 1.0, C.COULEUR_CANAPE, "plateforme"),
    "4": ("etagere", 1.0, C.COULEUR_BUFFET, "mur"),
    "5": ("television", 0.9, C.COULEUR_TELE, "decor"),
    "6": ("plante", 1.3, C.COULEUR_PLANTE, "decor"),
    "7": ("tapis", 0.12, C.COULEUR_TAPIS, "decor"),
    "8": ("maitresse", 1.2, C.COULEUR_MAITRESSE, "decor"),
    "9": ("rambarde", 0.8, C.COULEUR_RAMBARDE, "decor"),
    # elements accroches au mur : ils ne touchent jamais le chat
    "f": ("fenetre", 1.5, C.COULEUR_VERRE, "mural"),
    "c": ("cadre", 0.8, C.COULEUR_BUFFET, "mural"),
}


@dataclass
class Niveau:
    """Tout ce qu'un niveau contient, prêt pour le moteur de collisions."""

    titre: str = ""
    maitre: str = ""
    aide: str = ""
    largeur: float = 0.0
    hauteur: float = 0.0
    depart_chat: tuple = (0.0, 0.0)
    depart_maitre: tuple = (0.0, 0.0)
    reflexes_coupes: list = field(default_factory=list)

    murs: arcade.SpriteList = field(default_factory=lambda: arcade.SpriteList(use_spatial_hash=True))
    plateformes: arcade.SpriteList = field(default_factory=lambda: arcade.SpriteList(use_spatial_hash=True))
    mortels: arcade.SpriteList = field(default_factory=lambda: arcade.SpriteList(use_spatial_hash=True))
    poussables: arcade.SpriteList = field(default_factory=arcade.SpriteList)
    zones: arcade.SpriteList = field(default_factory=arcade.SpriteList)
    decor: arcade.SpriteList = field(default_factory=arcade.SpriteList)
    scriptes: dict = field(default_factory=dict)

    def dessiner(self) -> None:
        # le décor passe derrière tout le reste : il ne bloque jamais le chat
        self.decor.draw()
        self.murs.draw()
        self.plateformes.draw()
        self.zones.draw()
        self.mortels.draw()
        self.poussables.draw()

    def trouver_zone(self, role: str):
        """Retourne la première zone ayant ce rôle (``gamelle``, ``verre``...)."""
        for zone in self.zones:
            if getattr(zone, "role", "") == role:
                return zone
        return None


def chemin_du_niveau(numero: int):
    return C.DOSSIER_NIVEAUX / f"niveau_{numero}.txt"


def charger(numero: int) -> Niveau:
    """Lit ``niveaux/niveau_<numero>.txt`` et construit le niveau."""
    chemin = chemin_du_niveau(numero)
    if not chemin.is_file():
        raise FileNotFoundError(f"Niveau introuvable : {chemin}")

    lignes = chemin.read_text(encoding="utf-8").splitlines()
    if not lignes:
        raise ValueError(f"Niveau vide : {chemin}")

    metadonnees = json.loads(lignes[0])
    carte = [ligne for ligne in lignes[1:] if ligne.strip()]
    return construire(carte, metadonnees)


def construire(carte, metadonnees=None) -> Niveau:
    """Construit un niveau à partir d'une liste de lignes (pratique pour les tests)."""
    metadonnees = metadonnees or {}
    niveau = Niveau(
        titre=metadonnees.get("titre", ""),
        maitre=metadonnees.get("maitre", ""),
        aide=metadonnees.get("aide", ""),
        reflexes_coupes=metadonnees.get("reflexes_coupes", []),
    )

    tuile = C.TAILLE_TUILE
    nb_lignes = len(carte)
    niveau.hauteur = nb_lignes * tuile
    niveau.largeur = max(len(ligne) for ligne in carte) * tuile

    # 1re passe : le papier peint, sur toute la carte. Il doit etre pose avant
    # les meubles, sinon la case voisine repasse par-dessus une grande image.
    for numero_ligne, ligne in enumerate(carte):
        for colonne, caractere in enumerate(ligne):
            if caractere == C.CAR_MUR:
                continue
            x = colonne * tuile + tuile / 2
            y = (nb_lignes - 1 - numero_ligne) * tuile + tuile / 2
            sur_le_sol = (
                numero_ligne + 1 < nb_lignes
                and carte[numero_ligne + 1][colonne] == C.CAR_MUR
            )
            fond = _image("mur_bas" if sur_le_sol else "mur", x, y - tuile / 2)
            if fond is not None:
                niveau.decor.append(fond)

    # 2e passe : tout le reste
    for numero_ligne, ligne in enumerate(carte):
        for colonne, caractere in enumerate(ligne):
            # la 1re ligne du fichier est en haut, l'origine d'arcade est en bas
            x = colonne * tuile + tuile / 2
            y = (nb_lignes - 1 - numero_ligne) * tuile + tuile / 2
            _placer(niveau, caractere, x, y, carte, numero_ligne, colonne)

    return niveau


def _placer(niveau, caractere, x, y, carte=None, ligne=0, colonne=0) -> None:
    tuile = C.TAILLE_TUILE

    if caractere == C.CAR_MUR:
        bloc = _image(_nom_du_mur(carte, ligne, colonne), x, y - tuile / 2)
        if bloc is None:
            bloc = _carre(tuile, tuile, C.COULEUR_MUR, x, y, "mur")
        niveau.murs.append(bloc)

    elif caractere == C.CAR_PLATEFORME:
        image = _image(_morceau("balcon", carte, ligne, colonne), x,
                       y_haut=y + tuile / 2) if carte else None
        if image is not None:
            niveau.decor.append(image)
        # fine et posée en haut de la tuile : on passe dessous sans se cogner
        hauteur = tuile // 4
        couleur = (0, 0, 0, 0) if image is not None else C.COULEUR_PLATEFORME
        niveau.plateformes.append(
            _carre(tuile, hauteur, couleur, x, y + tuile / 2 - hauteur / 2, "plateforme")
        )

    elif caractere == C.CAR_MORTEL:
        hauteur = tuile // 2
        mortel = _carre(tuile, hauteur, C.COULEUR_MORTEL, x, y - tuile / 2 + hauteur / 2, "mortel")
        mortel.cause_de_mort = "les pointes"
        niveau.mortels.append(mortel)

    elif caractere == C.CAR_POUSSABLE:
        objet = _image("sac", x, y - tuile / 2)
        if objet is None:
            objet = _carre(tuile - 8, tuile - 8, C.COULEUR_POUSSABLE, x, y, "poussable")
        objet.amortit = True          # un pouf : il amortit les chutes
        niveau.poussables.append(objet)

    elif caractere == C.CAR_BOUTON:
        hauteur = tuile // 6
        bouton = _carre(tuile, hauteur, C.COULEUR_BOUTON, x, y - tuile / 2 + hauteur / 2, "bouton")
        bouton.role = "bouton"
        niveau.zones.append(bouton)

    elif caractere == C.CAR_PORTE:
        porte = _carre(tuile / 2, tuile, C.COULEUR_PORTE, x, y, "porte")
        porte.role = "porte"
        niveau.murs.append(porte)     # fermée = solide ; jeu.py l'ouvrira

    elif caractere == C.CAR_CHAT:
        niveau.depart_chat = (x, y)

    elif caractere == C.CAR_MAITRE:
        niveau.depart_maitre = (x, y)
        # TODO (maitre.py) : remplacer par la vraie classe Maitre
        daron = _image("daron", x, y - tuile / 2)
        if daron is None:
            daron = _carre(tuile, int(tuile * 1.2), C.COULEUR_MAITRE,
                           x, y - tuile / 2 + tuile * 1.2 / 2, "maitre")
        daron.nom = "maitre"
        niveau.decor.append(daron)

    elif caractere in MOBILIER:
        _placer_mobilier(niveau, caractere, x, y, carte, ligne, colonne)

    elif caractere in C.CARS_SCRIPTES:
        # laissé au responsable du niveau : il fera ce qu'il veut de ces positions
        niveau.scriptes.setdefault(caractere, []).append((x, y))


def _placer_mobilier(niveau, caractere, x, y, carte=None, ligne=0, colonne=0) -> None:
    """Pose un meuble.

    L'image va toujours dans ``decor`` ; la **forme de collision** est un
    rectangle invisible pose a cote. Les deux sont separes exprès : les pieds
    de la table en verre ne doivent pas bloquer le chat, seul son plateau
    compte.
    """
    tuile = C.TAILLE_TUILE
    nom, hauteur_tuiles, couleur, comportement = MOBILIER[caractere]
    invisible = (0, 0, 0, 0)

    hauteur = max(4, int(tuile * hauteur_tuiles))
    image = None
    if carte is not None:
        morceau = _morceau(nom, carte, ligne, colonne)
        # une image plus large qu'une case n'est dessinee que sur sa case gauche
        texture = _texture(morceau)
        if texture is not None and texture.width > 32:
            voisin_gauche = colonne > 0 and carte[ligne][colonne - 1] == caractere
            if voisin_gauche:
                niveau.scriptes.setdefault(caractere, []).append((x, y))
                return
            # elle demarre a gauche du groupe : on la recentre dessus
            x += (texture.width * ECHELLE_DECOR - tuile) / 2
        if comportement == "verre":
            image = _image(morceau, x, y_haut=y + tuile / 2)
        else:
            image = _image(morceau, x, y_bas=y - tuile / 2)
    if image is not None:
        niveau.decor.append(image)
        hauteur = image.height
        meuble = _carre(tuile, hauteur, invisible, x, y - tuile / 2 + hauteur / 2, nom)
    else:
        # pas encore d'image : on garde le rectangle de couleur, ça reste jouable
        meuble = _carre(tuile, hauteur, couleur, x, y - tuile / 2 + hauteur / 2, nom)
    meuble.nom = nom
    niveau.scriptes.setdefault(caractere, []).append((x, y))

    if comportement == "mural":
        # accroche au mur : le sprite est pose sur sa case, sans collision
        if image is None:
            niveau.decor.append(meuble)

    elif comportement == "decor":
        if image is None:
            niveau.decor.append(meuble)

    elif comportement == "plateforme":
        if image is None:
            niveau.decor.append(meuble)
        # on se pose sur le dessus du meuble, sans se cogner dedans par en bas
        dessus = _carre(tuile, tuile // 4, invisible if image is not None else couleur,
                        x, y + tuile / 2 - tuile / 8, nom + "_dessus")
        niveau.plateformes.append(dessus)

    elif comportement == "mur":
        # la collision reste une case pleine, quelle que soit l'image
        niveau.murs.append(_carre(tuile, tuile, invisible if image is not None else couleur,
                                  x, y, nom))

    elif comportement == "verre":
        # seul le plateau arrete le chat : les pieds ne sont que du dessin
        epaisseur = 8 if image is not None else hauteur
        plateau = _carre(
            tuile, epaisseur, invisible if image is not None else couleur,
            x, y + tuile / 2 - epaisseur / 2, nom
        )
        plateau.nom = nom
        niveau.plateformes.append(plateau)
        # la zone glissante déborde d'une tuile vers le haut, sinon le chat
        # posé dessus ne la touche pas (il est *au-dessus* du plateau)
        glisse = _carre(tuile, tuile, (0, 0, 0, 0), x, y + tuile / 2, nom + "_glisse")
        glisse.role = "verre"
        niveau.zones.append(glisse)

    elif comportement == "gamelle":
        meuble.role = "gamelle"
        meuble.remplie = False
        meuble.image = image          # pour la remplacer par la gamelle pleine
        niveau.zones.append(meuble)

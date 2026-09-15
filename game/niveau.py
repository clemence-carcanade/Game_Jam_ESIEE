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


#: certains décors ne se posent pas sur le bas de leur case : quelqu'un d'assis
#: doit descendre jusqu'à l'assise du canapé, sous la case du dessus.
DECALAGE = {"daron": -34, "maitresse": -34}

#: Deux sources d'images, dans cet ordre :
#:   assets/images/packs/  les packs achetes, decoupes par outils/importe_packs.py
#:                         (tuiles de 16 px, NON versionnes : voir leurs licences)
#:   assets/images/decor/  le decor dessine par outils/dessine_decor.py
#:                         (tuiles de 32 px, versionne, sert de secours)
#: Chaque image garde son echelle : une tuile de 16 px s'affiche x4, une de
#: 32 px s'affiche x2. Dans les deux cas, une tuile = une case du jeu.
DOSSIER_PACKS = C.DOSSIER_IMAGES / "packs"
DOSSIER_DECOR = C.DOSSIER_IMAGES / "decor"
ECHELLE_PACK = C.TAILLE_TUILE / 16
ECHELLE_DESSIN = C.TAILLE_TUILE / 32
ECHELLE_DECOR = ECHELLE_DESSIN          # garde le nom utilise ailleurs

_textures = {}
_echelles = {}


def _carre(largeur, hauteur, couleur, x, y, nom):
    """Un rectangle plein : sert de secours quand l'image n'existe pas encore,
    et de forme de collision invisible (couleur transparente)."""
    texture = arcade.Texture.create_empty(nom, (int(largeur), int(hauteur)), couleur)
    return arcade.Sprite(texture, center_x=x, center_y=y)


def _texture(nom):
    """Charge ``<nom>.png``, du pack en priorite, sinon du decor dessine."""
    if nom not in _textures:
        pack = DOSSIER_PACKS / f"{nom}.png"
        dessin = DOSSIER_DECOR / f"{nom}.png"
        if pack.is_file():
            _textures[nom] = arcade.load_texture(pack)
            _echelles[nom] = ECHELLE_PACK
        elif dessin.is_file():
            _textures[nom] = arcade.load_texture(dessin)
            _echelles[nom] = ECHELLE_DESSIN
        else:
            _textures[nom] = None
    return _textures[nom]


def _echelle(nom):
    """L'echelle d'affichage de cette image (x4 pour un pack, x2 pour un dessin)."""
    return _echelles.get(nom, ECHELLE_DESSIN)


def _image(nom, x, y_bas=None, y_haut=None):
    """Pose une image de décor. None si elle n'existe pas encore.

    On calcule le centre à partir de la hauteur de l'image, **jamais** avec
    ``sprite.bottom`` : arcade aligne alors la boîte de collision, qui ignore
    les pixels transparents. Une image à moitié vide se retrouverait décalée.
    """
    texture = _texture(nom)
    if texture is None:
        return None

    echelle = _echelle(nom)
    hauteur = texture.height * echelle
    sprite = arcade.Sprite(texture, scale=echelle, center_x=x)
    if y_haut is not None:
        sprite.center_y = y_haut - hauteur / 2
    else:
        sprite.center_y = y_bas + hauteur / 2 + DECALAGE.get(nom, 0)
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


def _voisin(carte, ligne, colonne, dl, dc):
    """Le caractère de la case voisine, ou None hors de la carte."""
    l, c = ligne + dl, colonne + dc
    if 0 <= l < len(carte) and 0 <= c < len(carte[l]):
        return carte[l][c]
    return None


def _coin_du_meuble(carte, ligne, colonne):
    """Cette case est-elle le coin bas-gauche du meuble ?

    Un canapé s'écrit avec 3 x 3 fois le même caractère. Une seule image est
    dessinée, depuis ce coin : sinon on empile neuf canapés.
    """
    ici = carte[ligne][colonne]
    return (
        _voisin(carte, ligne, colonne, 0, -1) != ici
        and _voisin(carte, ligne, colonne, 1, 0) != ici
    )


def _sommet_du_meuble(carte, ligne, colonne):
    """Cette case est-elle la rangée du dessus ? C'est là qu'on pose le pied."""
    return _voisin(carte, ligne, colonne, -1, 0) != carte[ligne][colonne]


def _largeur_du_meuble(carte, ligne, colonne):
    ici = carte[ligne][colonne]
    largeur = 1
    while _voisin(carte, ligne, colonne, 0, largeur) == ici:
        largeur += 1
    return largeur


def _morceau(nom, carte, ligne, colonne):
    """Choisit le morceau gauche / milieu / droite d'un meuble selon ses voisins.

    Un canapé de trois cases s'écrit ``333`` : la première prend ``canape_g``,
    la deuxième ``canape_m``, la troisième ``canape_d``. Rien à faire de plus
    dans le fichier de niveau.
    """
    # un pack fournit le meuble entier en une seule image : on la prefere
    # toujours aux morceaux gauche/milieu/droite du decor dessine.
    if (DOSSIER_PACKS / f"{nom}.png").is_file():
        return nom

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
    "2": ("table_basse", 1.0, C.COULEUR_VERRE, "verre"),
    "3": ("canape", 1.0, C.COULEUR_CANAPE, "plateforme"),
    "4": ("commode", 1.0, C.COULEUR_BUFFET, "mur"),
    "5": ("television", 0.9, C.COULEUR_TELE, "decor"),
    "6": ("plante", 1.3, C.COULEUR_PLANTE, "decor"),
    "7": ("tapis", 0.12, C.COULEUR_TAPIS, "decor"),
    "8": ("lampadaire", 1.2, C.COULEUR_MAITRESSE, "decor"),
    # accroches au mur : ils ne touchent jamais le chat
    "9": ("horloge", 0.8, C.COULEUR_RAMBARDE, "mural"),
    "f": ("miroir", 1.5, C.COULEUR_VERRE, "mural"),
    "c": ("tableau", 0.8, C.COULEUR_BUFFET, "mural"),
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
        # TODO (maitre.py) : le maitre n'est pas dessine pour l'instant. Les
        # personnages dessines a la main juraient avec les meubles du pack ;
        # c'est a celui qui fait maitre.py de fournir le bon sprite.

    elif caractere in MOBILIER:
        _placer_mobilier(niveau, caractere, x, y, carte, ligne, colonne)

    elif caractere in C.CARS_SCRIPTES:
        # laissé au responsable du niveau : il fera ce qu'il veut de ces positions
        niveau.scriptes.setdefault(caractere, []).append((x, y))


def _placer_mobilier(niveau, caractere, x, y, carte=None, ligne=0, colonne=0) -> None:
    """Pose un meuble : son image d'un cote, sa forme de collision de l'autre.

    Un meuble occupe souvent plusieurs cases (un canape, c'est 3 x 3 fois le
    meme caractere dans le fichier de niveau). Trois regles :

    * **l'image** n'est dessinee qu'une fois, depuis la case en bas a gauche du
      meuble, et centree sur toute sa largeur ;
    * **la collision** est posee case par case : un mur remplit chaque case,
      une plateforme ne se met que sur la rangee du dessus ;
    * les deux sont separees expres : les pieds d'une table ne doivent pas
      bloquer le chat, seul son plateau compte.

    Sans image disponible, on retombe sur un rectangle de couleur : le niveau
    reste jouable, il est juste moche.
    """
    tuile = C.TAILLE_TUILE
    nom, hauteur_tuiles, couleur, comportement = MOBILIER[caractere]
    invisible = (0, 0, 0, 0)

    niveau.scriptes.setdefault(caractere, []).append((x, y))

    # --- l'image ---
    texture = None
    if carte is not None:
        morceau = _morceau(nom, carte, ligne, colonne)
        texture = _texture(morceau)

        if texture is not None and _coin_du_meuble(carte, ligne, colonne):
            centre = x + (_largeur_du_meuble(carte, ligne, colonne) - 1) * tuile / 2
            plat = texture.height * _echelle(morceau) <= tuile
            if comportement == "verre" and plat:
                image = _image(morceau, centre, y_haut=y + tuile / 2)
            else:
                image = _image(morceau, centre, y_bas=y - tuile / 2)
            niveau.decor.append(image)

    avec_image = texture is not None
    teinte = invisible if avec_image else couleur

    if not avec_image and comportement in ("mural", "decor", "plateforme"):
        hauteur = max(4, int(tuile * hauteur_tuiles))
        secours = _carre(tuile, hauteur, couleur, x, y - tuile / 2 + hauteur / 2, nom)
        secours.nom = nom
        niveau.decor.append(secours)

    # --- la collision ---
    if comportement in ("mural", "decor"):
        return                              # on le traverse : rien a poser

    if comportement == "mur":
        niveau.murs.append(_carre(tuile, tuile, teinte, x, y, nom))
        return

    if carte is not None and not _sommet_du_meuble(carte, ligne, colonne):
        return                              # on ne pose le pied que sur le dessus

    if comportement == "plateforme":
        epaisseur = tuile // 4
        dessus = _carre(tuile, epaisseur, teinte, x, y + tuile / 2 - epaisseur / 2,
                        nom + "_dessus")
        niveau.plateformes.append(dessus)

    elif comportement == "verre":
        epaisseur = tuile // 6
        plateau = _carre(tuile, epaisseur, teinte, x, y + tuile / 2 - epaisseur / 2, nom)
        plateau.nom = nom
        niveau.plateformes.append(plateau)
        # la zone glissante deborde vers le haut : le chat est *au-dessus* du plateau
        glisse = _carre(tuile, tuile, invisible, x, y + tuile, nom + "_glisse")
        glisse.role = "verre"
        niveau.zones.append(glisse)

    elif comportement == "gamelle":
        hauteur = max(4, int(tuile * hauteur_tuiles))
        bol = _carre(tuile, hauteur, teinte, x, y - tuile / 2 + hauteur / 2, nom)
        bol.nom = nom
        bol.role = "gamelle"
        bol.remplie = False
        niveau.zones.append(bol)

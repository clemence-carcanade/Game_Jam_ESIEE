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
    """Sol, plafond, bordure ou mur ? On regarde la position et les voisins.

    Le pourtour de la piece est dessine en sombre ("bordure") : un mur qui a la
    meme couleur que le papier peint est un mur invisible, et un mur invisible
    est un bug pour celui qui joue. Seule la rangee du sol reste en parquet.
    """
    if carte is None:
        return "mur"

    def case(l, c):
        if 0 <= l < len(carte) and 0 <= c < len(carte[l]):
            return carte[l][c]
        return C.CAR_MUR

    dernier_l = len(carte) - 1
    if ligne == dernier_l and colonne not in (0, len(carte[ligne]) - 1):
        return "sol"
    if ligne in (0, dernier_l) or colonne in (0, len(carte[ligne]) - 1):
        return "bordure"
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
    "G": ("sortie", 1.0, C.COULEUR_GOAL if hasattr(C, "COULEUR_GOAL") else (120, 200, 140), "sortie"),
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
    "w": ("fenetre", 2.0, C.COULEUR_VERRE, "mural"),
    "b": ("bibliotheque", 1.0, C.COULEUR_BUFFET, "mur"),
    "p": ("porte", 4.0, C.COULEUR_BUFFET, "mural"),
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
    survivre: bool = False          # niveau 7 : mourir n'est plus le but
    piege_image: str = ""           # l'image de la zone mortelle (aquarium...)
    message_attente: str = ""       # E sur le piege pas encore arme
    docteur: bool = False           # niveau 6 : quelqu'un soigne toutes les morts
    objet_image: str = ""           # l'image de l'objet a pousser (somniferes...)
    fond: str = ""                  # l'image peinte qui sert de decor
    largeur: float = 0.0
    hauteur: float = 0.0
    depart_chat: tuple = (100.0, 100.0)
    point: object = None            # convertit ancre/pixels image -> ecran
    rampes: list = field(default_factory=list)   # pentes (x0,y0,x1,y1) en ecran
    pousseurs: list = field(default_factory=list)   # entites mobiles qui bousculent
    faux_pieges: dict = field(default_factory=dict)   # lettre -> effet scripte
    message_piege: str = ""         # ce qu'on lit quand le piege s'arme
    message_mort: str = ""          # ce qu'on lit en grillant une vie

    murs: arcade.SpriteList = field(default_factory=lambda: arcade.SpriteList(use_spatial_hash=True))
    plateformes: arcade.SpriteList = field(default_factory=lambda: arcade.SpriteList(use_spatial_hash=True))
    mortels: arcade.SpriteList = field(default_factory=lambda: arcade.SpriteList(use_spatial_hash=True))
    poussables: arcade.SpriteList = field(default_factory=arcade.SpriteList)
    zones: arcade.SpriteList = field(default_factory=arcade.SpriteList)
    decor: arcade.SpriteList = field(default_factory=arcade.SpriteList)
    scriptes: dict = field(default_factory=dict)

    def dessiner(self) -> None:
        # pixelated : sans ça, arcade lisse les textures agrandies et tout
        # devient flou. C'est le reglage qui fait "pixel art".
        self.decor.draw(pixelated=True)
        self.murs.draw(pixelated=True)
        self.plateformes.draw(pixelated=True)
        self.zones.draw(pixelated=True)
        self.mortels.draw(pixelated=True)
        self.poussables.draw(pixelated=True)

    def trouver_zone(self, role: str):
        """Retourne la première zone ayant ce rôle (``gamelle``, ``verre``...)."""
        for zone in self.zones:
            if getattr(zone, "role", "") == role:
                return zone
        return None


def charger(numero: int) -> Niveau:
    """Construit le niveau ``numero`` : la maison peinte + ce que le niveau y pose."""
    from game import les_niveaux

    if not 1 <= numero <= len(les_niveaux.NIVEAUX):
        raise ValueError(f"Pas de niveau {numero}")
    return construire_maison(les_niveaux.NIVEAUX[numero - 1], numero)


def construire_maison(definition, numero=1) -> Niveau:
    """La maison du niveau est le decor ; le niveau y pose ses acteurs.

    Chaque niveau a sa maison (game/maison.MAISONS) : son fond, sa taille et sa
    geometrie. Les positions sont en ancres nommees ou en pixels de l'image.
    """
    from game import maison as module_maison
    maison = module_maison.pour(numero)

    ech = C.LARGEUR_FENETRE / maison["largeur"]
    haut = maison["hauteur"]

    def x_de(px):
        return px * ech

    def y_de(py):
        return (haut - py) * ech

    def point(valeur):
        """Une ancre nommee, ou un couple (x, y) en pixels d'image."""
        if isinstance(valeur, str):
            valeur = maison["ancres"][valeur]
        return x_de(valeur[0]), y_de(valeur[1])

    invisible = (0, 0, 0, 0)
    niveau = Niveau(
        titre=definition.get("titre", ""),
        maitre=definition.get("maitre", ""),
        aide=definition.get("aide", ""),
        reflexes_coupes=definition.get("reflexes_coupes", []),
        survivre=definition.get("survivre", False),
        message_piege=definition.get("message_piege", ""),
        message_mort=definition.get("message_mort", ""),
        message_attente=definition.get("message_attente", ""),
        docteur=definition.get("docteur", False),
        objet_image=definition.get("objet_image", ""),
    )
    niveau.faux_pieges = definition.get("faux_pieges", {})
    niveau.pousseurs = definition.get("pousseurs", [])
    niveau.horde = definition.get("horde", False)
    niveau.flammes = definition.get("flammes", [])
    niveau.piege_direct = definition.get("piege_direct", False)
    niveau.camera = definition.get("camera", False)
    niveau.libelle_piege = definition.get("libelle_piege", "")
    cn = definition.get("chat_noir")
    niveau.chat_noir = point(cn) if cn else None
    fl = definition.get("fille")
    niveau.fille = point(fl) if fl else None
    niveau.fond = maison["fond"]
    niveau.largeur = maison["largeur"] * ech
    niveau.hauteur = maison["hauteur"] * ech
    x_depart, y_depart = point(definition.get("depart", "salon"))
    niveau.depart_chat = (x_depart, y_depart + 80)   # au-dessus du sol, il retombe
    niveau.point = point                     # les autres modules s'en servent

    # la geometrie de la maison, en rectangles invisibles calques sur l'image
    for x0, y0, x1, y1 in maison["solides"]:
        largeur, hauteur_r = (x1 - x0) * ech, (y1 - y0) * ech
        bloc = _carre(largeur, hauteur_r, invisible,
                      x_de((x0 + x1) / 2), y_de((y0 + y1) / 2) + hauteur_r / 2 - hauteur_r / 2, "solide")
        bloc.center_y = (y_de(y0) + y_de(y1)) / 2
        niveau.murs.append(bloc)
    for x0, y0, x1 in maison["plateformes"]:
        largeur = (x1 - x0) * ech
        plate = _carre(largeur, 10, invisible, x_de((x0 + x1) / 2), y_de(y0) - 5, "plateforme")
        niveau.plateformes.append(plate)
    niveau.rampes = [
        (x_de(x0), y_de(y0), x_de(x1), y_de(y1))
        for x0, y0, x1, y1 in maison.get("rampes", [])
    ]

    # l'objet a pousser
    if "objet" in definition:
        x, y = point(definition["objet"])
        objet = _image(definition.get("objet_image") or "sac", x, y_bas=y)
        if objet is None:
            objet = _carre(56, 56, C.COULEUR_POUSSABLE, x, y + 28, "objet")
        objet.bascule = definition.get("objet_anim") == "bascule"
        if not objet.bascule:
            objet.center_y += 30      # un peu au-dessus : il se cale en tombant
        objet.amortit = True
        niveau.poussables.append(objet)

    # le piege mortel (la "gamelle" generique)
    if "piege" in definition:
        x, y = point(definition["piege"])
        largeur = definition.get("piege_largeur", 110)
        zone = _carre(largeur, 64, invisible, x, y + 32, "piege")
        zone.role = "gamelle"
        zone.remplie = False
        image = _image(definition.get("piege_image", ""), x, y_bas=y)
        if image is not None:
            niveau.decor.append(image)
        niveau.zones.append(zone)

    # la sortie du dernier niveau
    if "sortie" in definition:
        x, y = point(definition["sortie"])
        zone = _carre(90, 110, invisible, x, y + 55, "sortie")
        zone.role = "sortie"
        niveau.zones.append(zone)

    # les elements mortels du niveau 7, avec leur image
    for element in definition.get("mortels", []):
        x, y = point(element["pos"])
        mortel = _carre(70, 40, invisible, x, y + 20, "mortel")
        mortel.cause_de_mort = element.get("cause", "le danger")
        niveau.mortels.append(mortel)
        image = _image(element.get("image", ""), x, y_bas=y)
        if image is not None:
            niveau.decor.append(image)

    return niveau


def construire(carte, metadonnees=None) -> Niveau:
    """Construit un niveau à partir d'une liste de lignes (pratique pour les tests)."""
    metadonnees = metadonnees or {}
    niveau = Niveau(
        titre=metadonnees.get("titre", ""),
        maitre=metadonnees.get("maitre", ""),
        aide=metadonnees.get("aide", ""),
        reflexes_coupes=metadonnees.get("reflexes_coupes", []),
        survivre=metadonnees.get("survivre", False),
        piege_image=metadonnees.get("piege_image", ""),
        message_attente=metadonnees.get("message_attente", ""),
        docteur=metadonnees.get("docteur", False),
        objet_image=metadonnees.get("objet_image", ""),
        message_piege=metadonnees.get("message_piege", ""),
        message_mort=metadonnees.get("message_mort", ""),
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
        objet = _image(niveau.objet_image or "sac", x, y - tuile / 2)
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

    elif caractere.islower() and caractere not in MOBILIER:
        # un emplacement scripte du niveau : les faux pieges, les personnages.
        # game/les_niveaux.py decrit ce que chaque lettre declenche.
        niveau.scriptes.setdefault(caractere, []).append((x, y))

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

    # la zone mortelle porte l'image de son niveau : l'aquarium de la chambre,
    # la marmite du restaurant, le cable de l'influenceur...
    if comportement == "gamelle" and niveau.piege_image:
        nom = niveau.piege_image
        if nom == "aucune":
            nom = "_zone_invisible"          # aucune texture : zone muette

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

    elif comportement == "sortie":
        hauteur = max(4, int(tuile * hauteur_tuiles))
        zone = _carre(tuile, hauteur, teinte, x, y - tuile / 2 + hauteur / 2, nom)
        zone.nom = nom
        zone.role = "sortie"
        niveau.zones.append(zone)

    elif comportement == "gamelle":
        hauteur = max(4, int(tuile * hauteur_tuiles))
        bol = _carre(tuile, hauteur, teinte, x, y - tuile / 2 + hauteur / 2, nom)
        bol.nom = nom
        bol.role = "gamelle"
        bol.remplie = False
        niveau.zones.append(bol)

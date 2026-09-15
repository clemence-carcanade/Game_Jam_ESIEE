"""Découpage de la planche de sprites du chat. [assets : Cat 50+ animations]

La planche ``assets/images/chat.png`` fait 256 x 1632 pixels : une grille de
8 colonnes sur 51 lignes, chaque case mesurant 32 x 32. Une ligne = une
animation, et toutes les lignes ne sont pas pleines.

On ne charge que les animations dont le jeu a besoin. Pour en ajouter une,
il suffit d'ajouter une entrée dans ``ANIMATIONS`` : ``(ligne, première image,
nombre d'images, durée d'une image en secondes, en boucle ou non)``.

Repères de la planche (relevés à l'oeil sur la planche fournie) :

    ligne  2   le chat debout, la queue qui bouge
    ligne 17   la marche
    ligne 46   la detente du saut (fin de ligne)
    ligne 47   la retombee puis la reception (debut de ligne)
    ligne 32   le chat allongé
    ligne 37   l'esprit qui s'eleve, puis le chat qui se reforme

Les lignes 34 a 36 existent aussi mais contiennent des pixels rouges : on ne
les utilise pas, le registre du jeu est cartoon (voir le brief).
"""

import arcade

from game import constantes as C

TAILLE_CASE = 32
COLONNES = 8

#: nom -> (ligne, première image, nombre d'images, durée d'une image, en boucle)
ANIMATIONS = {
    "repos":          (2, 0, 8, 0.12, True),
    "marche":         (17, 0, 8, 0.07, True),
    "saut":           (46, 5, 3, 0.09, False),
    "chute":          (47, 0, 3, 0.10, False),
    "reception":      (47, 3, 5, 0.06, False),
    "allonge":        (32, 0, 4, 0.18, True),
    "reincarnation":  (37, 0, 8, 0.10, False),
}

_planche = None
_cache = {}


def _charger_planche():
    global _planche
    if _planche is None:
        _planche = arcade.load_spritesheet(C.DOSSIER_IMAGES / "chat.png")
    return _planche


def images(nom, vers_la_gauche=False):
    """Retourne les textures d'une animation (chargées une seule fois).

    Le chat est dessiné tourné vers la droite sur la planche : on retourne les
    images quand il va à gauche.
    """
    cle = (nom, vers_la_gauche)
    if cle in _cache:
        return _cache[cle]

    if vers_la_gauche:
        _cache[cle] = [t.flip_left_right() for t in images(nom)]
        return _cache[cle]

    ligne, depart, nombre, _, _ = ANIMATIONS[nom]
    planche = _charger_planche()
    # get_texture_grid compte les cases depuis le début de la planche : on saute
    # les lignes précédentes, puis les premières cases de la ligne voulue.
    toutes = planche.get_texture_grid(
        size=(TAILLE_CASE, TAILLE_CASE),
        columns=COLONNES,
        count=(ligne + 1) * COLONNES,
    )
    debut = ligne * COLONNES + depart
    _cache[cle] = toutes[debut:debut + nombre]
    return _cache[cle]


def duree(nom):
    return ANIMATIONS[nom][3]


def en_boucle(nom):
    return ANIMATIONS[nom][4]


def boite_du_chat(nom="repos"):
    """Mesure le chat réellement dessiné dans ses cases (le reste est vide).

    Sans ça, la boîte de collision ferait 32 x 32 alors que le chat n'occupe
    qu'un petit rectangle en bas de la case : il flotterait au-dessus du sol et
    mourrait à cause d'un pixel transparent.

    Retourne (largeur, hauteur, décalage vertical) en pixels de la planche.
    """
    gauche, droite = TAILLE_CASE, 0
    haut, bas = TAILLE_CASE, 0
    for texture in images(nom):
        image = texture.image
        boite = image.getbbox()          # (gauche, haut, droite, bas), y vers le bas
        if boite is None:
            continue
        g, h, d, b = boite
        gauche, droite = min(gauche, g), max(droite, d)
        haut, bas = min(haut, h), max(bas, b)

    largeur = droite - gauche
    hauteur = bas - haut
    # centre du chat dans la case, en coordonnées sprite (y vers le haut)
    centre_y = TAILLE_CASE / 2 - (haut + bas) / 2
    return largeur, hauteur, centre_y

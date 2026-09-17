"""Les maisons : un fond peint et sa geometrie par niveau.

Chaque niveau a son propre decor (assets/images/fonds/) et sa geometrie de
collision, dans MAISONS[numero]. Toutes les coordonnees sont en pixels de
l'image (origine en haut a gauche) ; pour les relever, on ouvre l'image dans un
editeur et on lit la position au curseur.

Une maison declare :
    fond        le png dans assets/images/
    largeur/hauteur  la taille native de l'image
    solides     (x0, y0, x1, y1) murs et sol du bas, durs
    plateformes (x0, y0, x1) planchers/planches, traversables par le bas
    ancres      des points nommes (x, y du sol) ou poser les acteurs
"""

# --- niveau 1 : la maison d'origine -----------------------------------------
_M1 = dict(
    fond="fonds/maison.png", largeur=1672, hauteur=941,
    solides=[
        (40, 846, 1624, 878), (0, 32, 40, 878), (1624, 32, 1672, 878), (0, 20, 1672, 40),
    ],
    plateformes=[
        (40, 545, 388), (1234, 545, 1624), (40, 278, 1155), (1205, 266, 1624),
        (338, 494, 594), (654, 518, 908), (886, 430, 1038), (1138, 430, 1288),
        (668, 652, 828), (82, 662, 170), (655, 792, 840), (1006, 784, 1138),
        (66, 248, 354), (1300, 250, 1480), (494, 205, 600), (1494, 448, 1602),
        (1494, 368, 1602), (620, 560, 780), (860, 560, 1010), (1080, 470, 1240),
        (900, 385, 1080), (300, 400, 460), (200, 190, 420),
    ],
    ancres={
        "salon": (740, 846), "cuisine": (300, 846), "salle_droite": (1440, 846),
        "gamelle_bas": (1560, 846), "canape": (748, 792), "tv": (1072, 784),
        "frigo": (126, 662), "sdb": (200, 545), "chatterie": (1400, 545),
        "planche_sdb": (466, 494), "planche_centre": (780, 518),
        "planche_milieu_g": (962, 430), "planche_milieu_d": (1213, 430),
        "planche_salon": (748, 652), "arbre_bas": (1548, 448), "arbre_haut": (1548, 368),
        "chambre": (200, 278), "lit": (210, 248), "couloir": (760, 278),
        "armoire": (547, 205), "salle_haut": (1400, 266), "paniere": (1390, 250),
    },
)


def _trois_etages(fond, larg, haut, sols, plats, ancres):
    """Aide : assemble une maison a trois etages, sol du bas + murs deja poses."""
    solides = [
        (30, sols[0]-4, larg-30, sols[0]+28),      # sol du bas (dur)
        (0, 24, 30, haut-10), (larg-30, 24, larg, haut-10), (0, 12, larg, 30),
    ]
    plateformes = []
    # les planchers d'etage (traversables par le bas), pleine largeur
    for y in sols[1:]:
        plateformes.append((30, y, larg-30))
    plateformes += plats
    return dict(fond=fond, largeur=larg, hauteur=haut,
                solides=solides, plateformes=plateformes, ancres=ancres)


# Pour les niveaux 2 a 6, on releve les trois sols d'etage et les plateformes
# flottantes visibles sur le fond. Les ancres nommees pointent sur ces surfaces.

# --- niveau 2 : la vieille demeure (1774 x 887) -----------------------------
_M2 = _trois_etages(
    "fonds/niveau2.png", 1774, 887, sols=(830, 600, 300),
    plats=[
        (120, 380, 320), (150, 300, 300), (1420, 260, 1620),      # plateformes hautes
        (560, 380, 760), (700, 250, 900), (1180, 380, 1400),      # milieu
        (620, 620, 820), (1200, 700, 1420), (1480, 480, 1680),    # bas
        (900, 480, 1120), (300, 620, 480),
    ],
    ancres={
        "salon": (760, 830), "cuisine": (300, 600), "salle_droite": (1500, 830),
        "gamelle_bas": (1650, 830), "canape": (700, 620), "tv": (1300, 830),
        "frigo": (200, 380), "sdb": (250, 600), "chatterie": (1520, 600),
        "planche_sdb": (400, 380), "planche_centre": (800, 250),
        "planche_milieu_g": (1000, 480), "planche_milieu_d": (1290, 380),
        "planche_salon": (720, 620), "arbre_bas": (1580, 480), "arbre_haut": (1520, 260),
        "chambre": (300, 300), "lit": (300, 280), "couloir": (900, 300),
        "armoire": (700, 250), "salle_haut": (1520, 300), "paniere": (1520, 260),
    },
)

# Nouveaux fonds (1670 x 940) : geometrie relevee sur les rebords eclaires des
# images. Trois etages a y~300 / y~560-615 / y~860, plus des plateformes
# flottantes. Le sol du bas est solide, les etages sont traversables par le bas.

# --- niveau 3 : la chambre de l'enfant (pastel) ----------------------------
_M3 = dict(
    fond="fonds/niveau3.png", largeur=1670, hauteur=940,
    solides=[
        (30, 858, 1640, 890), (0, 30, 30, 905), (1640, 30, 1670, 905), (0, 14, 1670, 34),
    ],
    plateformes=[
        (40, 300, 1640),                                  # etage haut (chambre)
        (30, 558, 545), (545, 576, 1010), (1010, 556, 1420),   # etage milieu
        (150, 492, 370), (500, 444, 700), (800, 492, 995), (1250, 410, 1470),  # flottantes
    ],
    ancres={
        "salon": (300, 858), "cuisine": (560, 858), "salle_droite": (1080, 556),
        "gamelle_bas": (900, 858), "canape": (300, 858), "tv": (770, 858),
        "frigo": (250, 492), "sdb": (300, 558), "chatterie": (1330, 556),
        "planche_sdb": (600, 444), "planche_centre": (890, 492),
        "planche_milieu_g": (250, 492), "planche_milieu_d": (1350, 410),
        "planche_salon": (770, 576), "arbre_bas": (1300, 556), "arbre_haut": (1350, 410),
        "chambre": (250, 300), "lit": (200, 300), "couloir": (770, 300),
        "armoire": (1250, 300), "salle_haut": (1350, 300), "paniere": (1300, 300),
        "aquarium": (1130, 556),
    },
)

# --- niveau 4 : l'appart de l'influenceur -----------------------------------
_M4 = dict(
    fond="fonds/niveau4.png", largeur=1672, hauteur=940,
    solides=[
        (30, 858, 1642, 890), (0, 30, 30, 905), (1642, 30, 1672, 905), (0, 14, 1672, 34),
    ],
    plateformes=[
        (30, 297, 1642),                                  # etage haut
        (55, 544, 486), (491, 578, 855), (856, 556, 1180),
        (1186, 578, 1421), (1425, 556, 1615),             # etage milieu
        (366, 425, 519), (730, 425, 853), (543, 524, 726),
        (1201, 486, 1340), (579, 765, 742),               # flottantes
    ],
    ancres={
        "salon": (1150, 858), "cuisine": (500, 858), "salle_droite": (1520, 858),
        "gamelle_bas": (300, 858), "canape": (1150, 858), "tv": (1350, 858),
        "frigo": (400, 858), "sdb": (180, 544), "chatterie": (1520, 556),
        "planche_sdb": (440, 425), "planche_centre": (640, 524),
        "planche_milieu_g": (1000, 556), "planche_milieu_d": (1300, 578),
        "planche_salon": (670, 578), "arbre_bas": (1520, 556), "arbre_haut": (790, 425),
        "chambre": (200, 297), "lit": (200, 297), "couloir": (640, 297),
        "armoire": (490, 297), "salle_haut": (1300, 297), "paniere": (1300, 297),
    },
)

# --- niveau 5 : la cuisine du restaurant ------------------------------------
_M5 = dict(
    fond="fonds/niveau5.png", largeur=1672, hauteur=940,
    solides=[
        (30, 864, 1642, 894), (0, 30, 30, 905), (1642, 30, 1672, 905), (0, 14, 1672, 34),
    ],
    plateformes=[
        (40, 306, 1630),                                  # etage haut (salle)
        (40, 618, 596), (599, 630, 1035), (1042, 611, 1620),   # etage milieu (cuisine)
        (494, 448, 663), (1071, 418, 1208), (1317, 473, 1436),
        (156, 544, 299), (303, 572, 544), (668, 572, 971),
        (1123, 568, 1346), (608, 739, 782), (1143, 708, 1332),  # flottantes
    ],
    ancres={
        "salon": (300, 864), "cuisine": (500, 864), "salle_droite": (1400, 864),
        "gamelle_bas": (800, 864), "canape": (300, 618), "tv": (1250, 611),
        "frigo": (150, 864), "sdb": (220, 544), "chatterie": (1450, 611),
        "planche_sdb": (570, 448), "planche_centre": (820, 630),
        "planche_milieu_g": (1140, 418), "planche_milieu_d": (1370, 473),
        "planche_salon": (450, 572), "arbre_bas": (1230, 568), "arbre_haut": (1140, 306),
        "chambre": (400, 306), "lit": (400, 306), "couloir": (900, 306),
        "armoire": (1100, 306), "salle_haut": (1300, 306), "paniere": (1300, 306),
    },
)

# --- niveau 6 : le cabinet medical ------------------------------------------
_M6 = dict(
    fond="fonds/niveau6.png", largeur=1670, hauteur=940,
    solides=[
        (30, 866, 1640, 896), (0, 30, 30, 905), (1640, 30, 1670, 905), (0, 14, 1670, 34),
    ],
    plateformes=[
        (40, 302, 1620), (778, 197, 1043),                # etage haut + comptoir
        (40, 600, 300), (292, 614, 870), (1107, 606, 1620),    # etage milieu
        (278, 406, 368), (717, 405, 870), (1122, 405, 1279),
        (158, 496, 295), (929, 509, 1021), (636, 538, 796),
        (1344, 538, 1487), (932, 542, 1218), (56, 596, 289), (873, 596, 1103),
        (467, 687, 627), (1194, 705, 1347), (825, 747, 962), (418, 806, 560),  # flottantes
    ],
    ancres={
        "salon": (400, 866), "cuisine": (700, 866), "salle_droite": (1250, 866),
        "gamelle_bas": (700, 866), "canape": (400, 614), "tv": (1250, 606),
        "frigo": (200, 600), "sdb": (220, 496), "chatterie": (1450, 606),
        "planche_centre": (700, 614), "planche_milieu_g": (1000, 542),
        "planche_milieu_d": (1200, 405), "planche_salon": (600, 596),
        "arbre_bas": (1450, 606), "arbre_haut": (1150, 302),
        "chambre": (200, 302), "lit": (200, 302), "couloir": (700, 302),
        "armoire": (1150, 302), "salle_haut": (1400, 302), "paniere": (1400, 302),
    },
)

MAISONS = {1: _M1, 2: _M2, 3: _M3, 4: _M4, 5: _M5, 6: _M6}


def pour(numero):
    """La maison du niveau ``numero`` (1 par defaut si hors bornes)."""
    return MAISONS.get(numero, _M1)

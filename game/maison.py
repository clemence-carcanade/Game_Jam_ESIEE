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

# --- niveau 3 : la chambre de l'enfant (1365 x 768) ------------------------
_M3 = dict(
    fond="fonds/niveau3.png", largeur=1365, hauteur=768,
    solides=[
        (24, 700, 1340, 730), (0, 20, 24, 740), (1340, 20, 1365, 740), (0, 10, 1365, 24),
    ],
    plateformes=[
        (24, 235, 760), (810, 235, 1340),        # plancher etage 2 (coupe au milieu)
        (24, 465, 1340),                          # plancher etage 1
        (310, 215, 470), (620, 235, 770),         # plateformes etage 2
        (100, 430, 260), (400, 380, 580), (660, 415, 820),   # plateformes etage 1
        (980, 320, 1150), (1230, 320, 1340),
        (880, 660, 1130),                         # plateforme RDC droite
    ],
    ancres={
        "salon": (300, 700), "cuisine": (500, 700), "salle_droite": (1000, 660),
        "gamelle_bas": (1000, 660), "canape": (1000, 660), "tv": (700, 700),
        "frigo": (180, 430), "sdb": (490, 380), "chatterie": (1060, 320),
        "planche_sdb": (490, 380), "planche_centre": (740, 415),
        "planche_milieu_g": (180, 430), "planche_milieu_d": (1290, 320),
        "planche_salon": (740, 415), "arbre_bas": (1060, 320), "arbre_haut": (390, 215),
        "chambre": (200, 235), "lit": (200, 235), "couloir": (690, 235),
        "armoire": (390, 215), "salle_haut": (1000, 235), "paniere": (1010, 235),
        "aquarium": (1010, 200),
    },
)

# --- niveau 4 : l'appart de l'influenceur (1672 x 941) ----------------------
_M4 = _trois_etages(
    "fonds/niveau4.png", 1672, 941, sols=(870, 575, 300),
    plats=[
        (400, 195, 580), (700, 195, 900), (930, 195, 1100), (1180, 195, 1360),
        (330, 435, 500), (600, 435, 760), (1040, 435, 1200), (1300, 490, 1480),
        (280, 512, 450), (500, 555, 720), (860, 555, 1050),
        # tremplins pour monter du rez-de-chaussee a l'etage 1
        (150, 730, 350), (550, 730, 760), (960, 730, 1170), (1250, 720, 1400),
        (350, 650, 560), (760, 650, 970), (1100, 650, 1310),
    ],
    ancres={
        "salon": (1100, 870), "cuisine": (500, 870), "salle_droite": (1400, 870),
        "gamelle_bas": (300, 870), "canape": (1100, 870), "tv": (1350, 870),
        "frigo": (400, 870), "sdb": (200, 575), "chatterie": (1400, 575),
        "planche_sdb": (410, 435), "planche_centre": (680, 435),
        "planche_milieu_g": (1120, 435), "planche_milieu_d": (1390, 490),
        "planche_salon": (610, 555), "arbre_bas": (1400, 490), "arbre_haut": (1270, 195),
        "chambre": (200, 300), "lit": (200, 300), "couloir": (800, 300),
        "armoire": (490, 195), "salle_haut": (1270, 300), "paniere": (1270, 195),
    },
)

# --- niveau 5 : la cuisine du restaurant (1672 x 941) -----------------------
_M5 = _trois_etages(
    "fonds/niveau5.png", 1672, 941, sols=(830, 600, 320),
    plats=[
        (1000, 320, 1200),                                        # haut
        (120, 560, 320), (470, 470, 670), (1140, 430, 1340), (1360, 470, 1560),
        (300, 700, 500), (760, 720, 960), (1150, 680, 1350),
    ],
    ancres={
        "salon": (600, 830), "cuisine": (400, 600), "salle_droite": (1400, 830),
        "gamelle_bas": (700, 600), "canape": (400, 700), "tv": (1250, 680),
        "frigo": (200, 600), "sdb": (220, 560), "chatterie": (1450, 600),
        "planche_sdb": (570, 470), "planche_centre": (860, 720),
        "planche_milieu_g": (1240, 430), "planche_milieu_d": (1460, 470),
        "planche_salon": (400, 700), "arbre_bas": (1250, 680), "arbre_haut": (1100, 320),
        "chambre": (400, 320), "lit": (400, 320), "couloir": (900, 320),
        "armoire": (1100, 320), "salle_haut": (1300, 320), "paniere": (1300, 320),
    },
)

# --- niveau 6 : le cabinet medical (1672 x 941) -----------------------------
_M6 = _trois_etages(
    "fonds/niveau6.png", 1672, 941, sols=(870, 620, 300),
    plats=[
        (1050, 195, 1250),
        (60, 445, 230), (770, 415, 970), (1050, 415, 1220), (1360, 460, 1540),
        (60, 515, 230), (500, 575, 680), (270, 705, 490), (770, 745, 1000), (1150, 705, 1330),
    ],
    ancres={
        "salon": (700, 870), "cuisine": (400, 870), "salle_droite": (1400, 870),
        "gamelle_bas": (900, 870), "canape": (400, 705), "tv": (1240, 705),
        "frigo": (200, 620), "sdb": (150, 445), "chatterie": (1450, 620),
        "planche_centre": (880, 745), "planche_milieu_g": (1140, 415),
        "planche_milieu_d": (870, 415), "planche_salon": (590, 575),
        "arbre_bas": (1450, 460), "arbre_haut": (1150, 195),
        "chambre": (200, 300), "lit": (200, 300), "couloir": (700, 300),
        "armoire": (1150, 195), "salle_haut": (1400, 300), "paniere": (1400, 300),
    },
)

# --- niveau 7 : le jardin (1671 x 941) --------------------------------------
# deux niveaux : le jardin (herbe) en haut, la maison ouverte en bas.
_M7 = dict(
    fond="fonds/niveau7.png", largeur=1671, hauteur=941,
    solides=[
        (30, 796, 1641, 828), (0, 24, 30, 900), (1641, 24, 1671, 900), (0, 12, 1671, 30),
    ],
    plateformes=[
        (200, 448, 1400),                                         # le sol du jardin
        (480, 90, 720), (770, 180, 970), (1000, 330, 1200),       # flottantes du ciel
        (1100, 575, 1280), (450, 640, 620), (700, 790, 1060),     # flottantes de la maison
    ],
    ancres={
        "salon": (300, 796), "cuisine": (1300, 796), "salle_droite": (1300, 796),
        "gamelle_bas": (1350, 448), "canape": (550, 640), "tv": (880, 790),
        "frigo": (1400, 796), "sdb": (600, 448), "chatterie": (1000, 448),
        "planche_sdb": (600, 90), "planche_centre": (870, 180),
        "planche_milieu_g": (1100, 330), "planche_milieu_d": (1190, 575),
        "planche_salon": (535, 640), "arbre_bas": (1100, 330), "arbre_haut": (600, 90),
        "chambre": (400, 448), "lit": (300, 448), "couloir": (800, 448),
        "armoire": (600, 448), "salle_haut": (1200, 448), "paniere": (1150, 448),
    },
)

MAISONS = {1: _M1, 2: _M2, 3: _M3, 4: _M4, 5: _M5, 6: _M6, 7: _M7}


def pour(numero):
    """La maison du niveau ``numero`` (1 par defaut si hors bornes)."""
    return MAISONS.get(numero, _M1)

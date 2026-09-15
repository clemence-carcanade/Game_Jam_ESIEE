"""La maison : le fond peint et sa geometrie de collision.

``assets/images/fonds/maison.png`` EST le decor. Ce module trace par-dessus les
endroits ou le chat (et les autres) peuvent aller : les sols pleins, les
plateformes traversables (planches et meubles), et les ANCRES nommees.

Toutes les coordonnees sont en pixels de l'image (origine en haut a gauche) :
pour les relever, on ouvre l'image dans un editeur et on lit la position au
curseur. Trois etages, relies par les plateformes flottantes du milieu.
"""

FOND = "fonds/maison.png"
LARGEUR_IMAGE = 1672
HAUTEUR_IMAGE = 941

# --- les sols pleins et murs : on ne les traverse jamais --------------------
# (x gauche, y du dessus, x droite, y du dessous)
SOLIDES = [
    (40, 846, 1624, 878),        # le sol du rez-de-chaussee, d'un mur a l'autre
    (40, 545, 388, 572),         # le sol de la salle de bain (etage 1, gauche)
    (1234, 545, 1624, 572),      # le sol de la chatterie (etage 1, droite)
    (40, 278, 1155, 305),        # le sol de la chambre et du couloir (etage 2)
    (1205, 266, 1624, 294),      # le sol de la piece haute droite (etage 2)
    (0, 32, 40, 878),            # le mur exterieur gauche
    (1624, 32, 1672, 878),       # le mur exterieur droit
    (0, 20, 1672, 40),           # le plafond
]

# --- les plateformes traversables : on ne peut qu'atterrir dessus -----------
# (x gauche, y du dessus, x droite)
PLATEFORMES = [
    # les planches en bois eclairees, qui relient les etages
    (338, 494, 594),             # planche de la salle de bain
    (654, 518, 908),             # planche centrale basse
    (886, 430, 1038),            # planche du milieu, gauche
    (1138, 430, 1288),           # planche du milieu, droite
    (668, 652, 828),             # planche au-dessus du canape (salon)
    # les meubles sur lesquels on monte
    (82, 662, 170),              # le dessus du frigo (cuisine)
    (655, 792, 840),             # le canape du salon
    (1006, 784, 1138),           # le meuble tele
    (66, 248, 354),              # le lit de la chambre
    (1300, 250, 1480),           # le coussin de la piece haute droite
    (494, 205, 600),             # l'armoire du couloir (etage 2)
    # l'arbre a chat, a droite
    (1494, 448, 1602),           # plateforme du milieu
    (1494, 368, 1602),           # le sommet
    # --- tremplins ajoutes pour monter jusqu'au dernier etage ---
    (620, 560, 780),             # RDC -> vers l'etage 1 (au-dessus du canape)
    (860, 560, 1010),            # relais central
    (1080, 470, 1240),           # relais vers l'etage 2, centre-droit
    (900, 385, 1080),            # dernier tremplin sous le couloir de l'etage 2
    (300, 400, 460),             # une montee cote gauche (cuisine -> SdB -> etage 2)
    (200, 190, 420),             # SdB -> etage 2 gauche
]

# --- de quoi animer l'ambiance (pixels d'image) -----------------------------
# les lampes et plafonniers : ils respirent, un halo doux pulse dessus
LAMPES = [(505, 96), (1010, 165), (1355, 470), (1180, 700), (370, 622), (1470, 640)]
# les ecrans qui scintillent (television)
ECRANS = [(1072, 745)]
# ou passent les petits PNJ d'ambiance : (x gauche, x droite, y du sol)
PROMENADES = [
    (1300, 1470, 250),      # un chat sur le coussin de la piece haute droite
    (70, 340, 248),         # un chat sur le lit de la chambre
]
# la ou vole un papillon : (x centre, y centre, rayon)
PAPILLONS = [(780, 500, 90), (1450, 360, 70)]

# --- les endroits qui ont un nom (x, y du sol a cet endroit) -----------------
ANCRES = {
    # rez-de-chaussee
    "salon": (740, 846),
    "cuisine": (300, 846),
    "salle_droite": (1440, 846),
    "gamelle_bas": (1560, 846),
    "canape": (748, 792),
    "tv": (1072, 784),
    "frigo": (126, 662),
    # etage 1 (le milieu)
    "sdb": (200, 545),
    "chatterie": (1400, 545),
    "planche_sdb": (466, 494),
    "planche_centre": (780, 518),
    "planche_milieu_g": (962, 430),
    "planche_milieu_d": (1213, 430),
    "planche_salon": (748, 652),
    "arbre_bas": (1548, 448),
    "arbre_haut": (1548, 368),
    # etage 2 (le haut)
    "chambre": (200, 278),
    "lit": (210, 248),
    "couloir": (760, 278),
    "armoire": (547, 205),
    "salle_haut": (1400, 266),
    "paniere": (1390, 250),          # le coussin peint, en haut a droite
}

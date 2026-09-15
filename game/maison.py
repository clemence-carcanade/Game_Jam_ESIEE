"""La maison : le fond peint et sa geometrie de collision.

Le decor n'est plus construit en tuiles : ``assets/images/fonds/maison.png``
EST le niveau, et ce module decrit ou sont les sols, les murs et les meubles
sur lesquels on peut marcher. Toutes les coordonnees sont en **pixels de
l'image** (origine en haut a gauche, comme dans un editeur d'image) : pour les
relever, on ouvre l'image et on lit la position au curseur.

Les sept niveaux partagent cette maison ; seuls les antagonistes, l'objet a
pousser et le piege changent (voir les_niveaux.py). Les ANCRES nomment les
endroits utiles pour ne pas semer des nombres partout.
"""

FOND = "fonds/maison.png"
LARGEUR_IMAGE = 1672
HAUTEUR_IMAGE = 941

# --- les sols et murs pleins : on ne les traverse jamais --------------------
# (x gauche, y du dessus, x droite, y du dessous), en pixels de l'image
SOLIDES = [
    (28, 818, 1644, 852),        # le sol du rez-de-chaussee
    (28, 272, 1140, 302),        # le plancher chambre + couloir de l'etage
    (28, 545, 355, 575),         # le sol de la cuisine
    (330, 480, 592, 508),        # le palier en haut de l'escalier
    (700, 487, 1345, 512),       # la poutre au-dessus du salon
    (1345, 460, 1644, 490),      # le sol de la chatterie
    (1270, 185, 1596, 212),      # la corniche tout en haut a droite
    (0, 40, 28, 852),            # le mur exterieur gauche
    (1644, 40, 1672, 852),       # le mur exterieur droit
    (0, 28, 1672, 45),           # le plafond
    (1345, 212, 1368, 460),      # la cloison gauche de la chatterie
]

# --- les plateformes traversables : on ne peut qu'atterrir dessus -----------
# (x gauche, y du dessus, x droite)
PLATEFORMES = [
    (868, 400, 1032),            # plateforme flottante du couloir, gauche
    (1190, 400, 1345),           # plateforme flottante du couloir, droite
    (42, 380, 138),              # le dessus du frigo
    (148, 460, 288),             # le plan de travail de la cuisine
    (680, 700, 905),             # le canape du salon
    (975, 752, 1135),            # le meuble tele
    (198, 728, 318),             # la commode de l'entree
    (1368, 712, 1502),           # la table de la piece de droite
    (1408, 340, 1540),           # l'arbre a chat, plateforme du milieu
    (1398, 215, 1550),           # l'arbre a chat, sommet
]

# --- les rampes : on les monte en marchant, comme une pente -----------------
# (x gauche, y du sol a gauche, x droite, y du sol a droite), pixels d'image.
# L'escalier peint monte de la droite (bas, salon) vers la gauche (haut, palier).
RAMPES = [
    (430, 500, 720, 812),        # l'escalier salon -> palier de la cuisine
]

# --- les endroits qui ont un nom --------------------------------------------
# un point (x, y du sol a cet endroit) en pixels de l'image
ANCRES = {
    "salon": (620, 818),
    "entree": (120, 818),
    "gamelle_droite": (1595, 818),   # la gamelle peinte, en bas a droite
    "cuisine": (250, 545),
    "plan_travail": (218, 460),  # plan de travail (plateforme y=460)
    "frigo": (90, 380),          # dessus du frigo (plateforme y=380)
    "palier": (555, 480),
    "chambre": (170, 272),
    "couloir": (950, 272),
    "paniere": (1055, 272),          # la paniere peinte du couloir
    "poutre": (1000, 487),
    "poutre_gauche": (760, 487),
    "plateforme_gauche": (950, 400),
    "plateforme_droite": (1267, 400),
    "chatterie": (1500, 460),
    "chatterie_entree": (1385, 460),
    "arbre_milieu": (1474, 340),
    "arbre_haut": (1474, 215),
    "corniche": (1430, 185),
    "corniche_droite": (1550, 185),
    "canape": (790, 700),        # dessus du canape (plateforme y=700)
    "table_droite": (1435, 712), # table de droite (plateforme y=712)
}

"""Dessine le décor du jeu, pixel par pixel, dans assets/images/decor/.

    python outils/dessine_decor.py

Pourquoi un script plutôt que des PNG dessinés à la main : n'importe qui dans
l'équipe peut changer une couleur ou une forme ici et relancer, sans logiciel de
dessin. Les fichiers produits sont de vraies images, le jeu ne connaît que
celles-ci.

Style : tuiles de 32 x 32 pixels (affichées x2 dans le jeu, comme le chat),
palette limitée, contour sombre, lumière venant d'en haut à gauche.
"""

from pathlib import Path

from PIL import Image

DOSSIER = Path(__file__).resolve().parent.parent / "assets" / "images" / "decor"
TUILE = 32

# ---------------------------------------------------------------------------
# Palette du salon (change une valeur ici et tout le décor suit)
# ---------------------------------------------------------------------------
P = {
    "vide": (0, 0, 0, 0),
    "contour": (59, 41, 32),
    "ombre": (120, 100, 84),

    # murs : beige chaud, lambris clair en bas (comme dans un vrai salon)
    "mur": (242, 229, 175),
    "mur_clair": (250, 240, 200),
    "mur_sombre": (184, 175, 137),
    "lambris": (217, 217, 217),
    "lambris_clair": (230, 227, 227),
    "lambris_sombre": (180, 180, 180),

    # parquet miel
    "parquet": (184, 136, 75),
    "parquet_clair": (215, 175, 115),
    "parquet_sombre": (163, 120, 64),

    "bois": (136, 95, 66),
    "bois_clair": (168, 124, 88),
    "bois_sombre": (98, 66, 44),

    # canape beige
    "canape": (191, 161, 140),
    "canape_clair": (221, 197, 180),
    "canape_sombre": (136, 95, 66),

    "metal": (188, 188, 188),
    "metal_clair": (224, 224, 224),
    "metal_sombre": (140, 140, 140),

    "verre": (198, 226, 236, 140),
    "verre_clair": (238, 250, 255, 190),

    "ecran": (17, 12, 12),
    "ecran_bleu": (27, 138, 167),
    "pelouse": (86, 138, 78),
    "pelouse_clair": (118, 170, 104),

    "feuille": (74, 124, 76),
    "feuille_clair": (108, 164, 104),
    "pot": (176, 114, 82),

    "tapis": (230, 221, 215),
    "tapis_clair": (245, 240, 236),
    "tapis_sombre": (157, 145, 137),

    "croquette": (150, 96, 50),
    "croquette_clair": (184, 126, 70),
    "sac": (214, 186, 140),
    "sac_sombre": (176, 148, 106),

    "peau": (236, 194, 158),
    "cheveux": (72, 54, 46),
    "cheveux_f": (140, 78, 58),
    "pull_daron": (86, 116, 160),
    "pull_maitresse": (186, 104, 138),
    "jean": (68, 78, 110),

    "beton": (150, 146, 158),
    "beton_clair": (176, 172, 184),
    "ciel": (146, 196, 222),
}


class Toile:
    """Une petite image qu'on remplit pixel par pixel."""

    def __init__(self, largeur=TUILE, hauteur=TUILE):
        self.image = Image.new("RGBA", (largeur, hauteur), P["vide"])
        self.px = self.image.load()
        self.largeur = largeur
        self.hauteur = hauteur

    def point(self, x, y, couleur):
        if 0 <= x < self.largeur and 0 <= y < self.hauteur:
            self.px[int(x), int(y)] = P[couleur] if isinstance(couleur, str) else couleur

    def rect(self, x0, y0, x1, y1, couleur):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.point(x, y, couleur)

    def cadre(self, x0, y0, x1, y1, couleur):
        for x in range(int(x0), int(x1) + 1):
            self.point(x, y0, couleur)
            self.point(x, y1, couleur)
        for y in range(int(y0), int(y1) + 1):
            self.point(x0, y, couleur)
            self.point(x1, y, couleur)

    def ligne_h(self, y, x0, x1, couleur):
        self.rect(x0, y, x1, y, couleur)

    def ligne_v(self, x, y0, y1, couleur):
        self.rect(x, y0, x, y1, couleur)

    def enregistrer(self, nom):
        DOSSIER.mkdir(parents=True, exist_ok=True)
        self.image.save(DOSSIER / f"{nom}.png")
        return self.image


# ---------------------------------------------------------------------------
# Les murs et le sol
# ---------------------------------------------------------------------------
def mur():
    t = Toile()
    t.rect(0, 0, 31, 31, "mur")
    for x in range(5, 32, 11):
        t.ligne_v(x, 0, 31, "mur_clair")
    for x, y in ((3, 7), (14, 3), (27, 11), (9, 19), (21, 25), (30, 17), (17, 14)):
        t.point(x, y, "mur_sombre")
    return t.enregistrer("mur")


def mur_bas():
    """La rangee de mur qui touche le sol : lambris et plinthe."""
    t = Toile()
    t.rect(0, 0, 31, 9, "mur")
    for x in range(5, 32, 11):
        t.ligne_v(x, 0, 9, "mur_clair")
    # lambris
    t.rect(0, 10, 31, 31, "lambris")
    t.ligne_h(10, 0, 31, "lambris_clair")
    t.ligne_h(11, 0, 31, "lambris_sombre")
    for x in (0, 10, 21, 31):
        t.ligne_v(x, 12, 27, "lambris_sombre")
        t.ligne_v(min(x + 1, 31), 12, 27, "lambris_clair")
    # plinthe
    t.rect(0, 28, 31, 31, "lambris_sombre")
    t.ligne_h(28, 0, 31, "lambris_clair")
    return t.enregistrer("mur_bas")


def fenetre():
    """Une fenetre, pour que le haut du salon ne soit pas un mur vide."""
    t = Toile(64, 48)
    t.rect(0, 0, 63, 47, "bois")
    t.cadre(0, 0, 63, 47, "contour")
    t.rect(3, 3, 60, 44, "ciel")
    # reflets et croisillons
    t.rect(6, 6, 28, 20, (168, 210, 232))
    t.rect(34, 6, 57, 20, (168, 210, 232))
    t.rect(30, 3, 33, 44, "bois_clair")
    t.ligne_h(23, 3, 60, "bois_clair")
    t.ligne_h(24, 3, 60, "bois")
    t.cadre(3, 3, 60, 44, "bois_sombre")
    # rebord
    t.rect(0, 45, 63, 47, "bois_clair")
    return t.enregistrer("fenetre")


def cadre():
    """Un cadre au mur : la photo de famille, sans le chat dessus."""
    t = Toile(32, 26)
    t.rect(0, 0, 31, 25, "bois_sombre")
    t.cadre(0, 0, 31, 25, "contour")
    t.rect(3, 3, 28, 22, (236, 226, 206))
    # trois silhouettes
    t.rect(8, 12, 12, 21, "pull_daron")
    t.rect(9, 8, 11, 12, "peau")
    t.rect(15, 13, 19, 21, "pull_maitresse")
    t.rect(16, 9, 18, 13, "peau")
    t.rect(22, 16, 26, 21, "canape_sombre")
    t.cadre(3, 3, 28, 22, "bois_sombre")
    return t.enregistrer("cadre")


def sol():
    t = Toile()
    t.rect(0, 0, 31, 31, "parquet")
    t.ligne_h(0, 0, 31, "parquet_clair")      # la lumiere accroche le dessus
    # lames longues, un seul joint visible : sinon ca fait mur de briques
    t.ligne_h(11, 0, 31, "parquet_sombre")
    t.ligne_h(22, 0, 31, "parquet_sombre")
    t.ligne_h(12, 0, 31, "parquet_clair")
    t.ligne_h(23, 0, 31, "parquet_clair")
    # veines du bois
    for x0, x1, y in ((3, 12, 5), (18, 27, 7), (8, 20, 16), (22, 30, 18), (5, 14, 27)):
        t.ligne_h(y, x0, x1, "parquet_sombre")
    return t.enregistrer("sol")


def plafond():
    t = Toile()
    t.rect(0, 0, 31, 31, "lambris")
    t.ligne_h(0, 0, 31, "lambris_sombre")
    # corniche
    t.rect(0, 26, 31, 31, "lambris_clair")
    t.ligne_h(26, 0, 31, "lambris_sombre")
    t.ligne_h(31, 0, 31, "ombre")
    return t.enregistrer("plafond")


# ---------------------------------------------------------------------------
# Le canapé, en trois morceaux (gauche, milieu, droite)
# ---------------------------------------------------------------------------
def canape(partie):
    t = Toile()
    haut_dossier = 6
    # dossier
    t.rect(0, haut_dossier, 31, 20, "canape")
    t.ligne_h(haut_dossier, 0, 31, "canape_clair")
    # assise
    t.rect(0, 20, 31, 29, "canape_sombre")
    t.ligne_h(20, 0, 31, "canape_clair")
    # coussins
    if partie != "g":
        t.ligne_v(0, haut_dossier + 1, 28, "canape_sombre")
    if partie != "d":
        t.ligne_v(31, haut_dossier + 1, 28, "canape_sombre")
    # accoudoirs
    if partie == "g":
        t.rect(0, haut_dossier - 3, 6, 29, "canape")
        t.rect(0, haut_dossier - 3, 6, haut_dossier - 1, "canape_clair")
        t.cadre(0, haut_dossier - 3, 6, 29, "contour")
    if partie == "d":
        t.rect(25, haut_dossier - 3, 31, 29, "canape")
        t.rect(25, haut_dossier - 3, 31, haut_dossier - 1, "canape_clair")
        t.cadre(25, haut_dossier - 3, 31, 29, "contour")
    # pieds et contour
    t.rect(3, 30, 6, 31, "bois_sombre")
    t.rect(25, 30, 28, 31, "bois_sombre")
    t.ligne_h(haut_dossier - 1, 0, 31, "contour")
    t.ligne_h(29, 0, 31, "contour")
    if partie == "g":
        t.ligne_v(0, haut_dossier - 3, 29, "contour")
    if partie == "d":
        t.ligne_v(31, haut_dossier - 3, 29, "contour")
    return t.enregistrer(f"canape_{partie}")


# ---------------------------------------------------------------------------
# L'étagère murale (2 rangées x 3 morceaux) : le sac de croquettes est dessus
# ---------------------------------------------------------------------------
def etagere(partie, rangee):
    t = Toile()
    if rangee == "haut":
        t.rect(0, 0, 31, 5, "bois_clair")      # le plateau
        t.rect(0, 6, 31, 31, "bois")
        t.ligne_h(0, 0, 31, "bois_clair")
        t.ligne_h(6, 0, 31, "bois_sombre")
        # portes
        t.cadre(3, 10, 14, 29, "bois_sombre")
        t.cadre(17, 10, 28, 29, "bois_sombre")
        t.rect(12, 19, 13, 21, "metal_clair")  # poignées
        t.rect(18, 19, 19, 21, "metal_clair")
    else:
        t.rect(0, 0, 31, 24, "bois")
        t.rect(0, 25, 31, 27, "bois_sombre")
        t.ligne_h(28, 0, 31, "contour")
        # tiroirs
        t.cadre(3, 3, 28, 12, "bois_sombre")
        t.cadre(3, 14, 28, 23, "bois_sombre")
        t.rect(14, 7, 17, 8, "metal_clair")
        t.rect(14, 18, 17, 19, "metal_clair")
    if partie == "g":
        t.ligne_v(0, 0, 31, "contour")
    if partie == "d":
        t.ligne_v(31, 0, 31, "contour")
    if rangee == "haut":
        t.ligne_h(0, 0, 31, "contour")
    return t.enregistrer(f"etagere_{rangee}_{partie}")


# ---------------------------------------------------------------------------
# La table basse "en verre" (plateau + pieds)
# ---------------------------------------------------------------------------
def table_verre(partie):
    t = Toile()
    t.rect(0, 2, 31, 7, "verre")
    t.ligne_h(2, 0, 31, "verre_clair")
    t.ligne_h(4, 2, 12, "verre_clair")         # reflet
    t.ligne_h(7, 0, 31, "metal_sombre")
    t.ligne_h(1, 0, 31, "metal")
    if partie == "g":
        t.rect(3, 8, 5, 31, "metal")
        t.ligne_v(3, 8, 31, "metal_clair")
        t.ligne_v(5, 8, 31, "metal_sombre")
    if partie == "d":
        t.rect(26, 8, 28, 31, "metal")
        t.ligne_v(26, 8, 31, "metal_clair")
        t.ligne_v(28, 8, 31, "metal_sombre")
    return t.enregistrer(f"table_verre_{partie}")


# ---------------------------------------------------------------------------
# La télévision : le daron regarde le match
# ---------------------------------------------------------------------------
def television():
    t = Toile(32, 29)
    t.rect(1, 0, 30, 20, "ecran")
    t.rect(2, 1, 29, 19, "ecran_bleu")
    # le match : pelouse, ligne blanche, deux joueurs
    t.rect(2, 12, 29, 19, "pelouse")
    t.ligne_h(12, 2, 29, "pelouse_clair")
    t.ligne_v(16, 12, 19, "pelouse_clair")
    t.rect(9, 9, 10, 13, (230, 230, 240))
    t.rect(21, 10, 22, 13, (220, 90, 90))
    t.rect(3, 2, 12, 3, (86, 178, 202))        # reflet sur l'écran
    # pied
    t.rect(14, 21, 17, 25, "metal_sombre")
    t.rect(9, 26, 22, 28, "metal")
    t.ligne_h(26, 9, 22, "metal_clair")
    return t.enregistrer("television")


# ---------------------------------------------------------------------------
# La plante verte
# ---------------------------------------------------------------------------
def plante():
    t = Toile(32, 42)
    # pot
    t.rect(8, 30, 23, 41, "pot")
    t.ligne_h(30, 8, 23, (192, 116, 78))
    t.cadre(8, 30, 23, 41, "contour")
    t.rect(6, 27, 25, 30, "pot")
    t.cadre(6, 27, 25, 30, "contour")
    # feuillage
    feuilles = [
        (16, 4, 5), (10, 9, 5), (22, 9, 5), (7, 16, 4), (25, 16, 4),
        (13, 14, 5), (19, 14, 5), (16, 20, 5), (11, 22, 4), (21, 22, 4),
    ]
    for cx, cy, r in feuilles:
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + ((y - cy) * 1.4) ** 2 <= r * r:
                    t.point(x, y, "feuille")
        for y in range(cy - r, cy):
            for x in range(cx - r + 1, cx + 1):
                if (x - cx) ** 2 + ((y - cy) * 1.4) ** 2 <= (r - 1) ** 2:
                    t.point(x, y, "feuille_clair")
    t.rect(15, 20, 16, 29, "feuille")
    return t.enregistrer("plante")


# ---------------------------------------------------------------------------
# Le tapis
# ---------------------------------------------------------------------------
def tapis(partie):
    t = Toile(32, 9)
    t.rect(0, 2, 31, 8, "tapis")
    t.ligne_h(2, 0, 31, "tapis_clair")
    t.ligne_h(8, 0, 31, "tapis_sombre")
    # motif
    for x in range(2, 32, 8):
        t.rect(x, 4, x + 3, 6, "tapis_sombre")
        t.rect(x + 1, 5, x + 2, 5, "tapis_clair")
    # franges aux deux bouts
    if partie == "g":
        t.rect(0, 2, 1, 8, "tapis_sombre")
        for y in range(2, 9, 2):
            t.point(0, y, "tapis_clair")
    if partie == "d":
        t.rect(30, 2, 31, 8, "tapis_sombre")
        for y in range(2, 9, 2):
            t.point(31, y, "tapis_clair")
    return t.enregistrer(f"tapis_{partie}")


# ---------------------------------------------------------------------------
# La gamelle : vide, puis pleine des croquettes du fond du sac
# ---------------------------------------------------------------------------
def gamelle(pleine):
    t = Toile(32, 14)
    if pleine:
        t.rect(8, 3, 23, 7, "croquette")
        for x, y in ((10, 3), (14, 2), (18, 3), (21, 4), (12, 4), (16, 4)):
            t.point(x, y, "croquette_clair")
        # les petites vapeurs de ce qui ne se mange plus
        for x, y in ((7, 1), (16, 0), (25, 1)):
            t.point(x, y, (150, 180, 120))
    t.rect(6, 6, 25, 12, "metal")
    t.ligne_h(6, 6, 25, "metal_clair")
    t.rect(4, 5, 27, 7, "metal")
    t.ligne_h(5, 4, 27, "metal_clair")
    t.cadre(4, 5, 27, 12, "contour")
    t.ligne_h(13, 6, 25, "contour")
    return t.enregistrer("gamelle_pleine" if pleine else "gamelle_vide")


# ---------------------------------------------------------------------------
# Le sac de croquettes
# ---------------------------------------------------------------------------
def sac():
    t = Toile(28, 28)
    t.rect(2, 4, 25, 27, "sac")
    t.rect(2, 4, 25, 6, "sac_sombre")
    t.ligne_v(2, 4, 27, "sac_sombre")
    t.ligne_v(25, 4, 27, "sac_sombre")
    t.cadre(2, 4, 25, 27, "contour")
    # le haut roulé
    t.rect(5, 1, 22, 4, "sac_sombre")
    t.cadre(5, 1, 22, 4, "contour")
    # l'étiquette : une tête de chat
    t.rect(8, 10, 19, 21, "croquette")
    t.cadre(8, 10, 19, 21, "contour")
    t.rect(10, 13, 17, 19, "sac")
    t.rect(10, 12, 11, 13, "sac")
    t.rect(16, 12, 17, 13, "sac")
    t.point(12, 15, "contour")
    t.point(15, 15, "contour")
    t.rect(13, 17, 14, 17, "contour")
    return t.enregistrer("sac")


# ---------------------------------------------------------------------------
# Le balcon, sa rambarde, la baie vitrée
# ---------------------------------------------------------------------------
def balcon(partie):
    """Une etagere murale : la planche, et les equerres qui la tiennent.

    Sans les equerres, la planche a l'air de flotter en l'air.
    """
    t = Toile(32, 22)
    # la planche
    t.rect(0, 0, 31, 2, "bois_clair")
    t.rect(0, 3, 31, 8, "bois")
    t.rect(0, 9, 31, 10, "bois_sombre")
    for x0, x1, y in ((4, 14, 5), (18, 28, 7)):
        t.ligne_h(y, x0, x1, "bois_sombre")
    t.ligne_h(0, 0, 31, (178, 132, 88))

    # une equerre par morceau d'extremite, pour que ca tienne au mur
    def equerre(x):
        t.rect(x, 11, x + 2, 21, "metal_sombre")
        t.ligne_v(x, 11, 21, "metal")
        for i in range(9):                      # la diagonale de l'equerre
            t.point(x + 3 + i // 2, 12 + i, "metal_sombre")
    if partie == "g":
        equerre(4)
        t.ligne_v(0, 0, 10, "contour")
    elif partie == "d":
        equerre(25)
        t.ligne_v(31, 0, 10, "contour")
    return t.enregistrer(f"balcon_{partie}")


def rambarde():
    t = Toile(32, 26)
    t.rect(0, 0, 31, 2, "metal_clair")
    t.ligne_h(0, 0, 31, (200, 202, 216))
    for x in (4, 12, 20, 28):
        t.rect(x, 3, x + 1, 25, "metal")
        t.ligne_v(x, 3, 25, "metal_clair")
    t.rect(0, 12, 31, 13, "metal")
    return t.enregistrer("rambarde")


# ---------------------------------------------------------------------------
# Les habitants
# ---------------------------------------------------------------------------
def _personne(t, pull, cheveux, bras_leve):
    """Quelqu'un d'assis, vu de profil, tourne vers la tele (a gauche).

    Le bassin est en bas de l'image : le sprite se pose sur l'assise du canape,
    les jambes pendent devant. Debout, ca ne collerait jamais avec le canape.
    """
    # cuisses, a l'horizontale vers la gauche
    t.rect(4, 22, 20, 27, "jean")
    t.ligne_h(22, 4, 20, (84, 96, 132))
    t.cadre(4, 22, 20, 27, "contour")
    # mollets qui descendent, et les pieds
    t.rect(5, 28, 9, 33, "jean")
    t.cadre(5, 28, 9, 33, "contour")
    t.rect(2, 32, 9, 34, "contour")
    # torse
    t.rect(11, 9, 24, 23, pull)
    t.ligne_h(9, 11, 24, "contour")
    t.ligne_v(11, 9, 23, "contour")
    t.ligne_v(24, 9, 23, "contour")
    # tete
    t.rect(12, 0, 22, 9, "peau")
    t.cadre(12, 0, 22, 9, "contour")
    t.rect(12, 0, 22, 2, cheveux)
    t.cadre(12, 0, 22, 2, "contour")
    t.point(14, 5, "contour")                  # l'oeil, rive sur le match
    t.rect(13, 7, 15, 7, "contour")            # la bouche, ouverte
    # bras
    if bras_leve:
        t.rect(7, 4, 12, 6, pull)              # il gueule sur l arbitre
        t.cadre(7, 4, 12, 6, "contour")
        t.rect(4, 1, 8, 6, "peau")
        t.cadre(4, 1, 8, 6, "contour")
    else:
        t.rect(6, 13, 12, 16, pull)
        t.cadre(6, 13, 12, 16, "contour")
        t.rect(3, 13, 7, 16, "peau")
        t.cadre(3, 13, 7, 16, "contour")
    return t


def daron():
    t = Toile(32, 35)
    _personne(t, "pull_daron", "cheveux", bras_leve=True)
    return t.enregistrer("daron")


def maitresse():
    t = Toile(32, 35)
    _personne(t, "pull_maitresse", "cheveux_f", bras_leve=False)
    # cheveux plus longs, dans le dos
    t.rect(20, 2, 24, 12, "cheveux_f")
    t.cadre(20, 2, 24, 12, "contour")
    return t.enregistrer("maitresse")




# ---------------------------------------------------------------------------
# Les pieges et leurs figurants : chaque zone scriptee a son image.
# Sans elles, les pieges sont invisibles — un piege invisible n'existe pas.
# ---------------------------------------------------------------------------
def _figure(t, habit, cheveux, largeur=32):
    """Un personnage debout, de face : tete, buste, jambes. Iconique et lisible."""
    m = largeur // 2
    t.rect(m - 5, 26, m + 5, 36, "jean")            # jambes
    t.cadre(m - 5, 26, m + 5, 36, "contour")
    t.rect(m - 8, 12, m + 8, 26, habit)             # buste
    t.cadre(m - 8, 12, m + 8, 26, "contour")
    t.rect(m - 5, 2, m + 5, 12, "peau")             # tete
    t.cadre(m - 5, 2, m + 5, 12, "contour")
    t.rect(m - 5, 1, m + 5, 4, cheveux)
    t.point(m - 2, 7, "contour"); t.point(m + 2, 7, "contour")
    return t


def vieille():
    t = Toile(32, 38)
    _figure(t, (150, 130, 160), (210, 210, 215))
    t.rect(11, 1, 21, 3, (210, 210, 215))           # chignon gris
    t.rect(22, 18, 24, 36, "bois_sombre")           # la canne
    t.ligne_v(22, 18, 36, "bois_clair")
    # les charentaises, epaisses
    t.rect(9, 34, 15, 37, (200, 120, 130)); t.cadre(9, 34, 15, 37, "contour")
    t.rect(17, 34, 23, 37, (200, 120, 130)); t.cadre(17, 34, 23, 37, "contour")
    return t.enregistrer("vieille")


def enfant():
    t = Toile(32, 32)
    m = 16
    t.rect(m - 4, 22, m + 4, 30, (240, 200, 220))   # jupe
    t.cadre(m - 4, 22, m + 4, 30, "contour")
    t.rect(m - 6, 10, m + 6, 22, (250, 160, 190))
    t.cadre(m - 6, 10, m + 6, 22, "contour")
    t.rect(m - 4, 1, m + 4, 10, "peau")
    t.cadre(m - 4, 1, m + 4, 10, "contour")
    t.rect(m - 4, 0, m + 4, 3, (240, 220, 130))     # blonde
    # les couettes
    t.rect(m - 8, 2, m - 5, 9, (240, 220, 130)); t.cadre(m - 8, 2, m - 5, 9, "contour")
    t.rect(m + 5, 2, m + 8, 9, (240, 220, 130)); t.cadre(m + 5, 2, m + 8, 9, "contour")
    t.point(m - 2, 6, "contour"); t.point(m + 2, 6, "contour")
    return t.enregistrer("enfant")


def chef():
    t = Toile(32, 40)
    _figure(t, (245, 245, 245), "peau")
    t.rect(10, 0, 22, 6, (250, 250, 250))           # la toque
    t.cadre(10, 0, 22, 6, "contour")
    t.rect(12, 20, 20, 21, (200, 60, 60))           # le tablier noue
    return t.enregistrer("chef")


def medecin():
    t = Toile(32, 38)
    _figure(t, (240, 240, 248), "cheveux")
    t.rect(12, 14, 13, 24, (90, 160, 190))          # le stethoscope
    t.rect(18, 14, 19, 24, (90, 160, 190))
    t.rect(13, 23, 18, 25, (90, 160, 190))
    return t.enregistrer("medecin")


def chat_gris():
    t = Toile(24, 16)
    t.rect(2, 6, 17, 14, (150, 150, 158))           # le corps assis
    t.cadre(2, 6, 17, 14, "contour")
    t.rect(13, 1, 21, 9, (150, 150, 158))           # la tete
    t.cadre(13, 1, 21, 9, "contour")
    t.point(14, 0, (150, 150, 158)); t.point(20, 0, (150, 150, 158))  # oreilles
    t.point(16, 4, "contour"); t.point(19, 4, "contour")
    t.rect(0, 10, 2, 12, (150, 150, 158))           # la queue
    return t.enregistrer("chat_gris")


def panier_linge():
    t = Toile(28, 18)
    t.rect(2, 6, 25, 17, "sac")
    for x in range(4, 25, 4):
        t.ligne_v(x, 7, 16, "sac_sombre")
    t.cadre(2, 6, 25, 17, "contour")
    t.rect(5, 2, 12, 7, (230, 230, 240))            # le linge qui depasse
    t.rect(14, 3, 21, 7, (200, 220, 240))
    return t.enregistrer("panier_linge")


def maquillage():
    t = Toile(20, 14)
    t.rect(2, 6, 6, 13, (220, 70, 100))             # rouge a levres
    t.rect(2, 3, 6, 6, "metal_clair")
    t.cadre(2, 3, 6, 13, "contour")
    t.rect(10, 8, 18, 13, (240, 200, 220))          # poudrier
    t.cadre(10, 8, 18, 13, "contour")
    t.rect(12, 9, 16, 11, (250, 240, 245))
    return t.enregistrer("maquillage")


def griffures():
    t = Toile(24, 30)
    for x0 in (3, 9, 15):
        for i in range(24):
            t.point(x0 + i // 5, 3 + i, "mur_sombre")
    return t.enregistrer("griffures")


def couteau():
    t = Toile(26, 12)
    t.rect(2, 4, 15, 7, "metal_clair")              # la lame
    t.rect(2, 7, 15, 8, "metal_sombre")
    t.cadre(2, 4, 15, 8, "contour")
    t.rect(16, 3, 24, 9, "bois_sombre")             # le manche
    t.cadre(16, 3, 24, 9, "contour")
    return t.enregistrer("couteau")


def scalpel():
    t = Toile(22, 8)
    t.rect(1, 3, 9, 5, "metal_clair")
    t.rect(10, 2, 20, 6, "metal")
    t.cadre(1, 2, 20, 6, "contour")
    return t.enregistrer("scalpel")


def seringue():
    t = Toile(22, 10)
    t.rect(1, 4, 5, 5, "metal_sombre")              # l'aiguille
    t.rect(6, 2, 16, 8, (200, 230, 240))
    t.cadre(6, 2, 16, 8, "contour")
    t.rect(17, 3, 20, 7, "metal")
    t.rect(9, 4, 13, 6, (140, 200, 120))            # le produit
    return t.enregistrer("seringue")


def patient():
    t = Toile(32, 24)
    t.rect(1, 14, 30, 22, (230, 230, 240))          # le lit
    t.cadre(1, 14, 30, 22, "contour")
    t.rect(3, 8, 12, 15, (170, 210, 160))           # le patient, verdatre
    t.cadre(3, 8, 12, 15, "contour")
    t.point(6, 11, "contour"); t.point(9, 11, "contour")
    t.rect(5, 13, 10, 14, (250, 250, 250))          # le masque
    t.rect(13, 10, 29, 15, (200, 205, 220))         # la couverture
    return t.enregistrer("patient")


def papillon():
    t = Toile(16, 12)
    for dx in (0, 8):
        t.rect(2 + dx, 2, 6 + dx, 6, (240, 180, 90))
        t.rect(3 + dx, 6, 5 + dx, 9, (220, 140, 70))
        t.cadre(2 + dx, 2, 6 + dx, 9, "contour")
    t.rect(7, 3, 8, 9, "contour")                    # le corps
    return t.enregistrer("papillon")


def pelote():
    t = Toile(18, 16)
    for y in range(2, 14):
        for x in range(2, 16):
            if (x - 9) ** 2 + (y - 8) ** 2 <= 42:
                t.point(x, y, (200, 90, 110))
    for i in range(10):
        t.point(4 + i, 5 + (i % 3), (230, 130 ,150))
        t.point(5 + i, 9 + (i % 2), (160, 60, 80))
    return t.enregistrer("pelote")


def coussin():
    t = Toile(30, 12)
    t.rect(2, 3, 27, 10, (170, 120, 150))
    t.ligne_h(3, 2, 27, (200, 150, 180))
    t.cadre(2, 3, 27, 10, "contour")
    return t.enregistrer("coussin")


def aquarium():
    t = Toile(32, 22)
    t.rect(1, 2, 30, 20, (140, 200, 225, 200))
    t.cadre(1, 2, 30, 20, "contour")
    t.ligne_h(4, 2, 29, (200, 240, 250))            # la surface
    t.rect(8, 10, 13, 14, (240, 140, 80))           # le poisson
    t.point(7, 12, (240, 140, 80)); t.point(14, 11, "contour")
    t.rect(22, 14, 24, 19, "feuille")               # une algue
    return t.enregistrer("aquarium")


def cable():
    t = Toile(32, 14)
    for i in range(22):
        t.point(2 + i, 9 + (i % 4 == 0), "contour")
        t.point(2 + i, 10 + (i % 4 == 0), (60, 60, 70))
    t.rect(23, 4, 30, 12, (60, 60, 70))             # la prise
    t.cadre(23, 4, 30, 12, "contour")
    t.point(20, 6, (255, 230, 90))                  # ca gresille
    t.point(18, 3, (255, 230, 90)); t.point(22, 2, (255, 200, 60))
    return t.enregistrer("cable")


def marmite():
    t = Toile(30, 20)
    t.rect(2, 6, 27, 18, "metal_sombre")
    t.ligne_h(6, 2, 27, "metal")
    t.cadre(2, 6, 27, 18, "contour")
    t.rect(0, 8, 2, 10, "metal"); t.rect(27, 8, 29, 10, "metal")
    for x, y in ((7, 3), (13, 1), (19, 3), (10, 4), (16, 2)):
        t.point(x, y, (240, 240, 250))              # la vapeur
    return t.enregistrer("marmite")


def somniferes():
    t = Toile(18, 20)
    t.rect(5, 1, 13, 4, "metal_sombre")             # le bouchon
    t.rect(3, 5, 15, 18, (150, 190, 230))
    t.cadre(3, 5, 15, 18, "contour")
    t.rect(5, 8, 13, 14, (240, 245, 250))           # l'etiquette
    t.rect(7, 10, 8, 12, "contour")                 # une lune
    t.point(9, 10, "contour")
    return t.enregistrer("somniferes")


def defibrillateur():
    t = Toile(26, 18)
    t.rect(2, 4, 23, 16, (210, 60, 60))
    t.cadre(2, 4, 23, 16, "contour")
    t.rect(5, 7, 12, 13, (240, 240, 245))           # l'ecran
    # l'eclair
    for i, (x, y) in enumerate(((8, 8), (9, 9), (8, 10), (9, 11), (10, 12))):
        t.point(x, y, (240, 200, 60))
    t.rect(15, 7, 20, 9, "metal_clair")             # les palettes
    t.rect(15, 11, 20, 13, "metal_clair")
    return t.enregistrer("defibrillateur")


def medicaments():
    t = Toile(24, 26)
    t.rect(2, 2, 21, 24, (240, 240, 245))           # l'armoire a pharmacie
    t.cadre(2, 2, 21, 24, "contour")
    t.rect(9, 6, 14, 19, (210, 60, 60))             # la croix
    t.rect(5, 11, 18, 15, (210, 60, 60))
    t.ligne_h(24, 2, 21, "contour")
    return t.enregistrer("medicaments")


def arbre_chat_objet():
    """Un petit arbre a chat : c'est lui qui bascule sur le chat au niveau 2."""
    t = Toile(28, 44)
    t.rect(4, 40, 23, 43, "bois_sombre")            # la base
    t.cadre(4, 40, 23, 43, "contour")
    t.rect(11, 10, 16, 40, (214, 200, 176))         # le poteau (sisal)
    for y in range(11, 40, 3):
        t.ligne_h(y, 11, 16, (188, 172, 150))
    t.cadre(11, 10, 16, 40, "contour")
    t.rect(2, 4, 25, 11, (200, 186, 162))           # la plateforme du haut
    t.cadre(2, 4, 25, 11, "contour")
    t.rect(9, 0, 18, 5, (150, 150, 158))            # la boule/coussin
    t.cadre(9, 0, 18, 5, "contour")
    return t.enregistrer("arbre_chat_objet")


def jouet_bain():
    t = Toile(22, 18)
    t.rect(4, 6, 17, 15, (240, 210, 70))            # le corps du canard
    t.cadre(4, 6, 17, 15, "contour")
    t.rect(13, 2, 19, 8, (240, 210, 70))            # la tete
    t.cadre(13, 2, 19, 8, "contour")
    t.rect(18, 5, 21, 7, (230, 140, 60))            # le bec
    t.point(15, 4, "contour")                       # l'oeil
    return t.enregistrer("jouet_bain")


def ring_light():
    t = Toile(30, 40)
    for y in range(2, 22):                           # l'anneau lumineux
        for x in range(2, 28):
            d = (x - 15) ** 2 + (y - 12) ** 2
            if 90 <= d <= 150:
                t.point(x, y, (250, 245, 210))
            elif 150 < d <= 175:
                t.point(x, y, "contour")
    t.rect(14, 22, 16, 37, "metal_sombre")          # le pied
    t.rect(9, 37, 21, 39, "metal")
    t.cadre(9, 37, 21, 39, "contour")
    return t.enregistrer("ring_light")


def couvercle():
    t = Toile(30, 14)
    for x in range(2, 28):                            # le dome
        h = int(2 + (1 - abs(x - 15) / 14) * 6)
        for y in range(12 - h, 12):
            t.point(x, y, "metal")
        t.point(x, 12 - h, "metal_clair")
    t.rect(2, 11, 27, 13, "metal_sombre")            # le bord
    t.cadre(2, 11, 27, 13, "contour")
    t.rect(13, 1, 16, 4, "metal_sombre")             # la poignee
    return t.enregistrer("couvercle")


# ---------------------------------------------------------------------------
# Dangers "evidents" qui ratent : de quoi voir plein de facons de mourir.
# ---------------------------------------------------------------------------
def prise():
    t = Toile(18, 18)
    t.rect(2, 2, 15, 15, (235, 235, 240))
    t.cadre(2, 2, 15, 15, "contour")
    t.point(7, 7, "contour"); t.point(10, 7, "contour")   # les trous
    t.rect(7, 10, 10, 11, "contour")
    t.point(5, 3, (255, 220, 90)); t.point(13, 5, (255, 200, 60))  # etincelles
    return t.enregistrer("prise")


def fenetre_ouverte():
    t = Toile(30, 34)
    t.rect(2, 2, 27, 31, (60, 66, 96))              # le ciel de nuit
    t.cadre(2, 2, 27, 31, "bois")
    t.rect(2, 2, 27, 6, "bois")                     # le battant releve
    t.ligne_v(14, 6, 31, "bois")
    for x,y in ((7,12),(20,9),(12,20),(23,24)): t.point(x,y,(230,230,245))  # etoiles
    return t.enregistrer("fenetre_ouverte")


def four():
    t = Toile(28, 26)
    t.rect(2, 2, 25, 24, (200, 200, 208))
    t.cadre(2, 2, 25, 24, "contour")
    t.rect(5, 9, 22, 21, (40, 30, 30))             # la porte vitree
    t.cadre(5, 9, 22, 21, "contour")
    t.rect(8, 14, 19, 19, (230, 120, 50))          # les flammes
    t.rect(10, 12, 17, 15, (245, 190, 70))
    t.rect(6, 4, 9, 6, "contour"); t.rect(12, 4, 15, 6, "contour")  # boutons
    return t.enregistrer("four")


def poison():
    t = Toile(18, 24)
    t.rect(6, 1, 11, 5, "metal_sombre")            # le bouchon
    t.rect(3, 6, 14, 22, (110, 160, 90))           # la bouteille
    t.cadre(3, 6, 14, 22, "contour")
    t.rect(6, 10, 11, 18, (230, 230, 235))         # l'etiquette
    t.point(8, 12, "contour"); t.point(9, 12, "contour")   # tete de mort
    t.rect(7, 14, 10, 15, "contour")
    return t.enregistrer("poison")


def gaz():
    t = Toile(24, 26)
    t.rect(6, 8, 17, 24, (210, 90, 60))            # la bonbonne
    t.cadre(6, 8, 17, 24, "contour")
    t.rect(9, 4, 14, 8, "metal_sombre")            # la valve
    t.rect(10, 1, 13, 4, "metal")
    for x,y in ((3,6),(19,4),(2,12)): t.point(x,y,(200,220,200))   # fuite
    return t.enregistrer("gaz")


def cordelette():
    t = Toile(20, 22)
    for i in range(18):
        t.point(9 + (i%3==0), 2+i, "sac_sombre")   # la corde qui pend
        t.point(10 + (i%3==0), 2+i, "sac")
    t.rect(6, 18, 13, 21, "sac_sombre")            # un noeud coulant en bas
    t.cadre(6, 18, 13, 21, "contour")
    return t.enregistrer("cordelette")


def bougie():
    t = Toile(16, 22)
    t.rect(5, 8, 10, 20, (235, 225, 200))          # la cire
    t.cadre(5, 8, 10, 20, "contour")
    t.rect(7, 4, 8, 8, "contour")                  # la meche
    t.rect(6, 0, 9, 5, (245, 190, 70))             # la flamme
    t.point(7, 1, (255, 230, 120))
    return t.enregistrer("bougie")


def verre_casse():
    t = Toile(24, 14)
    for x0 in (3, 10, 17):
        for i in range(6):
            t.point(x0 + i - i//2, 12 - i, (180, 220, 230))
            t.point(x0 + i - i//2, 13 - i, "contour")
    t.rect(2, 12, 22, 13, (150, 190, 200))         # les debris au sol
    return t.enregistrer("verre_casse")


# ---------------------------------------------------------------------------
def tout_dessiner():
    mur(); mur_bas(); sol(); plafond(); fenetre(); cadre()
    for partie in "gmd":
        canape(partie); table_verre(partie); tapis(partie); balcon(partie)
        etagere(partie, "haut"); etagere(partie, "bas")
    television(); plante(); sac(); rambarde(); daron(); maitresse()
    vieille(); enfant(); chef(); medecin(); chat_gris(); panier_linge()
    maquillage(); griffures(); couteau(); scalpel(); seringue(); patient()
    papillon(); pelote(); coussin(); aquarium(); cable(); marmite()
    somniferes(); defibrillateur(); medicaments()
    arbre_chat_objet(); jouet_bain(); ring_light(); couvercle()
    prise(); fenetre_ouverte(); four(); poison(); gaz(); cordelette(); bougie(); verre_casse()
    gamelle(False); gamelle(True)
    fichiers = sorted(p.name for p in DOSSIER.glob("*.png"))
    print(f"{len(fichiers)} images ecrites dans {DOSSIER} :")
    print("  " + ", ".join(fichiers))


if __name__ == "__main__":
    tout_dessiner()

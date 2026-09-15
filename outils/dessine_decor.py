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
    "contour": (38, 30, 44),
    "ombre": (58, 46, 66),

    "mur": (72, 62, 92),
    "mur_clair": (84, 74, 106),
    "mur_sombre": (60, 52, 78),
    "plinthe": (96, 84, 120),

    "parquet": (122, 84, 56),
    "parquet_clair": (146, 104, 70),
    "parquet_sombre": (96, 64, 42),

    "bois": (128, 88, 52),
    "bois_clair": (158, 112, 70),
    "bois_sombre": (92, 60, 34),

    "canape": (150, 74, 84),
    "canape_clair": (178, 96, 106),
    "canape_sombre": (110, 52, 60),

    "metal": (140, 142, 158),
    "metal_clair": (178, 180, 196),
    "metal_sombre": (96, 98, 114),

    "verre": (168, 214, 232, 150),
    "verre_clair": (224, 244, 252, 190),

    "ecran": (40, 48, 62),
    "pelouse": (72, 132, 74),
    "pelouse_clair": (96, 160, 96),

    "feuille": (66, 132, 78),
    "feuille_clair": (92, 170, 102),
    "pot": (164, 92, 60),

    "tapis": (128, 76, 106),
    "tapis_clair": (160, 104, 136),

    "croquette": (138, 88, 44),
    "croquette_clair": (168, 114, 62),
    "sac": (206, 178, 132),
    "sac_sombre": (168, 140, 98),

    "peau": (232, 186, 148),
    "cheveux": (62, 46, 40),
    "cheveux_f": (128, 70, 52),
    "pull_daron": (74, 104, 150),
    "pull_maitresse": (176, 90, 128),
    "jean": (58, 66, 96),

    "beton": (118, 114, 128),
    "beton_clair": (142, 138, 152),
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
    # papier peint : rayures tres discretes, sinon ca mange tout l'ecran
    for x in range(5, 32, 11):
        t.ligne_v(x, 0, 31, "mur_clair")
    # quelques points de matiere
    for x, y in ((3, 7), (14, 3), (27, 11), (9, 19), (21, 25), (30, 17), (17, 14)):
        t.point(x, y, "mur_sombre")
    return t.enregistrer("mur")


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
    t.rect(0, 0, 31, 31, "mur_sombre")
    t.ligne_h(31, 0, 31, "plinthe")
    t.ligne_h(30, 0, 31, "contour")
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
    t.rect(1, 0, 30, 20, "contour")
    t.rect(2, 1, 29, 19, "ecran")
    # le match : pelouse, ligne blanche, deux joueurs
    t.rect(2, 12, 29, 19, "pelouse")
    t.ligne_h(12, 2, 29, "pelouse_clair")
    t.ligne_v(16, 12, 19, "pelouse_clair")
    t.rect(9, 9, 10, 13, (230, 230, 240))
    t.rect(21, 10, 22, 13, (220, 90, 90))
    t.rect(3, 2, 12, 3, (70, 82, 102))         # reflet sur l'écran
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
    t = Toile(32, 8)
    t.rect(0, 2, 31, 7, "tapis")
    t.ligne_h(2, 0, 31, "tapis_clair")
    for x in range(1, 32, 6):
        t.rect(x, 4, x + 2, 5, "tapis_clair")
    if partie == "g":
        t.rect(0, 2, 1, 7, "tapis_clair")
    if partie == "d":
        t.rect(30, 2, 31, 7, "tapis_clair")
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
    """Une planche : sert de balcon dehors, d'etagere murale dedans."""
    t = Toile(32, 14)
    t.rect(0, 0, 31, 2, "bois_clair")
    t.rect(0, 3, 31, 11, "bois")
    t.rect(0, 12, 31, 13, "bois_sombre")
    for x0, x1, y in ((4, 14, 6), (18, 28, 8)):
        t.ligne_h(y, x0, x1, "bois_sombre")
    t.ligne_h(0, 0, 31, (178, 132, 88))
    if partie == "g":
        t.ligne_v(0, 0, 13, "contour")
    if partie == "d":
        t.ligne_v(31, 0, 13, "contour")
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
    """Une personne assise, vue de profil, tournée vers la télé (à gauche)."""
    # jambes
    t.rect(2, 26, 18, 31, "jean")
    t.ligne_h(26, 2, 18, (76, 86, 120))
    t.cadre(2, 26, 18, 31, "contour")
    # torse
    t.rect(10, 12, 24, 27, pull)
    t.ligne_v(10, 12, 27, "contour")
    t.ligne_h(12, 10, 24, "contour")
    t.ligne_v(24, 12, 27, "contour")
    # tête
    t.rect(11, 2, 22, 12, "peau")
    t.cadre(11, 2, 22, 12, "contour")
    t.rect(11, 1, 22, 4, cheveux)
    t.cadre(11, 1, 22, 4, "contour")
    t.point(13, 7, "contour")                 # l'oeil, rivé sur le match
    t.rect(12, 10, 14, 10, "contour")         # la bouche, ouverte
    # bras
    if bras_leve:
        t.rect(6, 6, 11, 8, pull)             # il gueule sur l'arbitre
        t.cadre(6, 6, 11, 8, "contour")
        t.rect(4, 4, 7, 8, "peau")
        t.cadre(4, 4, 7, 8, "contour")
    else:
        t.rect(5, 16, 12, 19, pull)
        t.cadre(5, 16, 12, 19, "contour")
        t.rect(3, 16, 6, 19, "peau")
        t.cadre(3, 16, 6, 19, "contour")
    return t


def daron():
    t = Toile(32, 38)
    _personne(t, "pull_daron", "cheveux", bras_leve=True)
    return t.enregistrer("daron")


def maitresse():
    t = Toile(32, 38)
    _personne(t, "pull_maitresse", "cheveux_f", bras_leve=False)
    # cheveux plus longs
    t.rect(19, 4, 23, 14, "cheveux_f")
    t.cadre(19, 4, 23, 14, "contour")
    return t.enregistrer("maitresse")


# ---------------------------------------------------------------------------
def tout_dessiner():
    mur(); sol(); plafond()
    for partie in "gmd":
        canape(partie); table_verre(partie); tapis(partie); balcon(partie)
        etagere(partie, "haut"); etagere(partie, "bas")
    television(); plante(); sac(); rambarde(); daron(); maitresse()
    gamelle(False); gamelle(True)
    fichiers = sorted(p.name for p in DOSSIER.glob("*.png"))
    print(f"{len(fichiers)} images ecrites dans {DOSSIER} :")
    print("  " + ", ".join(fichiers))


if __name__ == "__main__":
    tout_dessiner()

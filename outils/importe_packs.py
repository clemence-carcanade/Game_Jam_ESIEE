"""Découpe le décor dans les packs achetés, vers assets/images/packs/.

    python outils/importe_packs.py

**Les fichiers produits ne sont pas versionnés** : le dépôt est public et les
licences des packs interdisent d'y redistribuer leurs images. Chaque membre de
l'équipe télécharge les packs de son côté, les pose dans son dossier de
téléchargements, puis lance ce script une fois.

Si le dossier `assets/images/packs/` est vide, le jeu retombe automatiquement
sur le décor dessiné par `outils/dessine_decor.py`, qui lui est versionné.

Packs utilisés :
    pixelinterior_LRK_v1.1  (Bitglow) — murs, sols, canapé, télé, tapis, meubles
"""

from pathlib import Path

from PIL import Image

SOURCE = Path.home() / "Downloads"
DESTINATION = Path(__file__).resolve().parent.parent / "assets" / "images" / "packs"
TUILE = 16

#: nom voulu -> (planche, colonne, rangée, largeur, hauteur) en tuiles de 16 px
DECOUPES = {

    # gros meubles
    "canape":       ("livingroom_LRK.png", 1, 1, 3, 3),
    "commode":      ("livingroom_LRK.png", 1, 9, 3, 3),
    "table_basse":  ("livingroom_LRK.png", 36, 11, 2, 2),
    "television":   ("livingroom_LRK.png", 22, 23, 3, 2),
    "tapis":        ("livingroom_LRK.png", 21, 18, 4, 1),

    # décoration
    "bibliotheque": ("cabinets_LRK.png", 1, 1, 3, 3),
    "vaisselier":   ("cabinets_LRK.png", 13, 1, 3, 3),
    "fenetre":      ("doorswindowsstairs_LRK.png", 13, 1, 3, 2),
    "porte":        ("doorswindowsstairs_LRK.png", 7, 1, 2, 4),

    "plante":       ("decorations_LRK.png", 1, 5, 1, 2),
    "tableau":      ("decorations_LRK.png", 7, 6, 2, 1),
    "horloge":      ("decorations_LRK.png", 1, 8, 1, 1),
    "lampadaire":   ("decorations_LRK.png", 1, 1, 1, 3),
    "miroir":       ("decorations_LRK.png", 10, 4, 1, 3),
}


#: Les aplats de mur et de sol sont dessines en gros blocs entoures d'un liseré.
#: Une tuile prise sur la grille contient donc un bout de ce liseré, et le jeu
#: affiche un quadrillage. On decoupe ces quatre-la au pixel pres, en plein
#: milieu du bloc : nom -> (planche, x, y) du coin haut-gauche, 16 x 16.
DECOUPES_PIXEL = {
    "mur":     ("floorswalls_LRK.png", 34, 22),
    "mur_bas": ("floorswalls_LRK.png", 20, 52),
    "sol":     ("floorswalls_LRK.png", 34, 88),
    "plafond": ("floorswalls_LRK.png", 34, 22),
    "bordure": ("floorswalls_LRK.png", 162, 88),
}


def dossier_du_pack():
    for candidat in SOURCE.glob("pixelinterior*"):
        if candidat.is_dir():
            return candidat
    return None


def importer():
    pack = dossier_du_pack()
    if pack is None:
        print(f"Pack introuvable dans {SOURCE}. Le jeu gardera le decor dessine.")
        return 0

    DESTINATION.mkdir(parents=True, exist_ok=True)
    planches = {}
    ecrits = 0

    for nom, (fichier, colonne, rangee, largeur, hauteur) in DECOUPES.items():
        chemin = pack / fichier
        if not chemin.is_file():
            print(f"  manquant : {fichier}")
            continue
        if fichier not in planches:
            planches[fichier] = Image.open(chemin).convert("RGBA")

        boite = (
            colonne * TUILE, rangee * TUILE,
            (colonne + largeur) * TUILE, (rangee + hauteur) * TUILE,
        )
        planches[fichier].crop(boite).save(DESTINATION / f"{nom}.png")
        ecrits += 1

    for nom, (fichier, x, y) in DECOUPES_PIXEL.items():
        chemin = pack / fichier
        if not chemin.is_file():
            continue
        if fichier not in planches:
            planches[fichier] = Image.open(chemin).convert("RGBA")
        planches[fichier].crop((x, y, x + TUILE, y + TUILE)).save(DESTINATION / f"{nom}.png")
        ecrits += 1

    print(f"{ecrits} images decoupees dans {DESTINATION}")
    print("Rappel : ce dossier est ignore par Git, les licences l'interdisent.")
    return ecrits


if __name__ == "__main__":
    importer()

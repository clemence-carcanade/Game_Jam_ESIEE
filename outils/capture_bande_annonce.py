"""Capture du gameplay pour la bande-annonce.

On joue chaque niveau a pas de temps fixe (30 images/seconde), en injectant
des entrees scriptees directement dans la vue, et on enregistre chaque image
en PNG dans trailer/public/gameplay/niveau_N/. Comme le temps est simule, le
resultat est fluide meme si l'enregistrement est lent.

    venv/bin/python outils/capture_bande_annonce.py 2
    venv/bin/python outils/capture_bande_annonce.py       # tous les scenarios
"""

import shutil
import sys
from pathlib import Path

import arcade

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game import audio, constantes as C            # noqa: E402
from game.jeu import VueJeu                        # noqa: E402

DOSSIER_SORTIE = Path(__file__).resolve().parent.parent / "trailer/public/gameplay"

# La physique du jeu est en pixels par tick a 60 i/s (voir constantes.py) : on
# simule donc des ticks de 1/60 s et on garde une image sur deux, pour une
# lecture a 30 i/s a la vraie vitesse du jeu.
CADENCE = 1 / 60.0
TICKS_PAR_IMAGE = 2

# Un scenario = la liste des entrees, en ticks : (tick, "appui"/"relache", touche).
# Le SPACE du tick 0 saute l'ecran de transition du niveau.
SCENARIOS = {
    2: {
        "duree": 240,
        "entrees": [
            (0, "appui", arcade.key.SPACE), (1, "relache", arcade.key.SPACE),
            (10, "appui", arcade.key.D),
            (60, "appui", arcade.key.SPACE), (76, "relache", arcade.key.SPACE),
            (124, "appui", arcade.key.SPACE), (140, "relache", arcade.key.SPACE),
            (190, "appui", arcade.key.SPACE), (206, "relache", arcade.key.SPACE),
        ],
    },
    3: {
        "duree": 240,
        "entrees": [
            (0, "appui", arcade.key.SPACE), (1, "relache", arcade.key.SPACE),
            (10, "appui", arcade.key.D),
            (50, "appui", arcade.key.SPACE), (66, "relache", arcade.key.SPACE),
            (110, "appui", arcade.key.SPACE), (126, "relache", arcade.key.SPACE),
            (170, "appui", arcade.key.SPACE), (186, "relache", arcade.key.SPACE),
        ],
    },
    5: {
        "duree": 240,
        "entrees": [
            (0, "appui", arcade.key.SPACE), (1, "relache", arcade.key.SPACE),
            (10, "appui", arcade.key.D),
            (70, "appui", arcade.key.SPACE), (86, "relache", arcade.key.SPACE),
            (140, "appui", arcade.key.SPACE), (156, "relache", arcade.key.SPACE),
        ],
    },
}


def capturer(fenetre: arcade.Window, numero: int, scenario: dict) -> None:
    dossier = DOSSIER_SORTIE / f"niveau_{numero}"
    if dossier.exists():
        shutil.rmtree(dossier)
    dossier.mkdir(parents=True)

    vue = VueJeu(numero)
    fenetre.show_view(vue)

    for tick in range(scenario["duree"]):
        for quand, mode, touche in scenario["entrees"]:
            if quand == tick:
                if mode == "appui":
                    vue.on_key_press(touche, 0)
                else:
                    vue.on_key_release(touche, 0)
        vue.on_update(CADENCE)
        if tick % TICKS_PAR_IMAGE:
            continue
        vue.on_draw()
        # L'ecran retina rend en 2x : on redescend a la taille logique, en JPEG,
        # sinon la capture pese un gigaoctet.
        image = arcade.get_image().convert("RGB")
        image = image.resize((C.LARGEUR_FENETRE, C.HAUTEUR_FENETRE))
        image.save(dossier / f"frame_{tick // TICKS_PAR_IMAGE:04d}.jpg", quality=88)
        fenetre.flip()

    print(f"niveau {numero} : {scenario['duree'] // TICKS_PAR_IMAGE} images -> {dossier}")


def principal() -> None:
    audio.VOLUME = 0.0                    # pas de son pendant la capture
    numeros = [int(a) for a in sys.argv[1:]] or sorted(SCENARIOS)

    fenetre = arcade.Window(
        C.LARGEUR_FENETRE, C.HAUTEUR_FENETRE, "capture bande-annonce",
        vsync=False,
    )
    for numero in numeros:
        capturer(fenetre, numero, SCENARIOS[numero])
    fenetre.close()


if __name__ == "__main__":
    principal()

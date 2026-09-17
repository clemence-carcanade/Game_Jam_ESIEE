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
CADENCE = 1 / 30.0

# Un scenario = la liste des entrees, en frames : (frame, "appui"/"relache", touche).
# Le SPACE de la frame 0 saute l'ecran de transition du niveau.
SCENARIOS = {
    2: {
        "duree": 120,
        "entrees": [
            (0, "appui", arcade.key.SPACE), (1, "relache", arcade.key.SPACE),
            (5, "appui", arcade.key.D),
            (30, "appui", arcade.key.SPACE), (38, "relache", arcade.key.SPACE),
            (62, "appui", arcade.key.SPACE), (70, "relache", arcade.key.SPACE),
            (95, "appui", arcade.key.SPACE), (103, "relache", arcade.key.SPACE),
        ],
    },
    3: {
        "duree": 120,
        "entrees": [
            (0, "appui", arcade.key.SPACE), (1, "relache", arcade.key.SPACE),
            (5, "appui", arcade.key.D),
            (25, "appui", arcade.key.SPACE), (33, "relache", arcade.key.SPACE),
            (55, "appui", arcade.key.SPACE), (63, "relache", arcade.key.SPACE),
            (85, "appui", arcade.key.SPACE), (93, "relache", arcade.key.SPACE),
        ],
    },
    5: {
        "duree": 120,
        "entrees": [
            (0, "appui", arcade.key.SPACE), (1, "relache", arcade.key.SPACE),
            (5, "appui", arcade.key.D),
            (35, "appui", arcade.key.SPACE), (43, "relache", arcade.key.SPACE),
            (70, "appui", arcade.key.SPACE), (78, "relache", arcade.key.SPACE),
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

    for frame in range(scenario["duree"]):
        for quand, mode, touche in scenario["entrees"]:
            if quand == frame:
                if mode == "appui":
                    vue.on_key_press(touche, 0)
                else:
                    vue.on_key_release(touche, 0)
        vue.on_update(CADENCE)
        vue.on_draw()
        arcade.get_image().save(dossier / f"frame_{frame:04d}.png")
        fenetre.flip()

    print(f"niveau {numero} : {scenario['duree']} frames -> {dossier}")


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

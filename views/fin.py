"""L'ecran de fin : la petite video qui cloture le jeu, puis retour au menu.

La video est pre-decoupee en images (assets/videos/fin/f####.jpg) avec sa piste
audio a part (assets/sons/fin.mp3) : aucune dependance a ffmpeg au lancement, ca
tourne partout. On affiche le flipbook a la cadence d'origine (meta.txt), cale
sur l'horloge (si l'affichage rame, on saute des images mais le son reste juste).

Le rendu passe par une unique texture GL mise a jour en place (comme la mise a
l'echelle plein ecran de main.py) : memoire constante, quel que soit le nombre
d'images.
"""

import time

import arcade
from arcade.gl import geometry
from PIL import Image

from game import constantes as C
from game import audio as _audio

_DOSSIER = C.DOSSIER_ASSETS / "videos" / "fin"


def _lire_meta():
    """(fps, nombre d'images, largeur, hauteur) depuis meta.txt, avec secours."""
    try:
        vals = (_DOSSIER / "meta.txt").read_text().split()
        return float(vals[0]), int(vals[1]), int(vals[2]), int(vals[3])
    except Exception:
        n = len(list(_DOSSIER.glob("f*.jpg")))
        return 24.0, n, 960, 540


class FinView(arcade.View):
    """Joue la video de fin en plein cadre, puis rend la main au menu."""

    def __init__(self):
        super().__init__()
        self.fps, self.nb_images, self.larg, self.haut = _lire_meta()
        self._debut = None
        self._index = -1
        self._son = None
        self._lecteur = None
        self._prog = None
        self._quad = None
        self._texture = None
        self._fini = False

    # -- ressources GL creees quand le contexte est courant -----------------
    def _preparer_gl(self):
        ctx = self.window.ctx
        self._prog = ctx.utility_textured_quad_program
        self._quad = geometry.quad_2d_fs()
        self._texture = ctx.texture(
            (self.larg, self.haut), components=3,
            filter=(ctx.LINEAR, ctx.LINEAR))

    def _charger_image(self, i):
        """Envoie l'image i dans la texture GL (retournee : origine GL en bas)."""
        chemin = _DOSSIER / f"f{i:04d}.jpg"
        if not chemin.is_file():
            return
        im = Image.open(chemin).convert("RGB")
        if im.size != (self.larg, self.haut):
            im = im.resize((self.larg, self.haut), Image.LANCZOS)
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
        self._texture.write(im.tobytes())

    # -- cycle de vue --------------------------------------------------------
    def on_show_view(self):
        self.window.set_mouse_visible(False)
        self.window.background_color = (0, 0, 0)
        if self._texture is None:
            self._preparer_gl()
        # premiere image tout de suite (pas d'ecran noir au demarrage)
        self._index = 0
        self._charger_image(0)
        # la piste audio, calee sur le meme depart que les images
        chemin_son = C.DOSSIER_SONS / "fin.mp3"
        if chemin_son.is_file() and not _audio.VOLUME == 0:
            try:
                self._son = arcade.Sound(chemin_son)
                self._lecteur = arcade.play_sound(self._son, volume=_audio.VOLUME)
            except Exception as e:
                print(f"[fin] audio indisponible : {e}")
        self._debut = time.perf_counter()

    def on_hide_view(self):
        self._arreter_son()

    def _arreter_son(self):
        if self._lecteur is not None:
            try:
                arcade.stop_sound(self._lecteur)
            except Exception:
                pass
            self._lecteur = None

    def _vers_menu(self):
        if self._fini:
            return
        self._fini = True
        self._arreter_son()
        from views.menu import MenuView
        self.window.show_view(MenuView())

    def on_update(self, delta_time):
        if self._debut is None:
            return
        ecoule = time.perf_counter() - self._debut
        cible = int(ecoule * self.fps)
        if cible >= self.nb_images:
            self._vers_menu()
            return
        if cible != self._index:
            self._index = cible
            self._charger_image(cible)

    def on_draw(self):
        self.clear()
        if self._texture is not None:
            self._texture.use(0)
            self._quad.render(self._prog)

    # passer la video : Espace / Entree / Echap
    def on_key_press(self, touche, modificateurs):
        if touche in (arcade.key.SPACE, arcade.key.ENTER, arcade.key.RETURN,
                      arcade.key.ESCAPE):
            self._vers_menu()

    def on_mouse_press(self, x, y, bouton, modificateurs):
        self._vers_menu()

"""Sept Vies -- point d'entree.

    python main.py            plein ecran (menu puis jeu)
    python main.py fenetre    en fenetre (1408 x 792)
    python main.py 3          directement le niveau 3 (debug)
    python main.py 3 fenetre  niveau 3, en fenetre

F11 bascule plein ecran / fenetre a tout moment.
"""

import sys

import arcade
from arcade.gl import geometry

from game import constantes as C
from game.jeu import VueJeu


class FenetreJeu(arcade.Window):
    """Fenetre plein ecran.

    Le jeu est toujours dessine dans un espace logique fixe de 1408 x 792, puis
    mis a l'echelle vers l'ecran (avec bandes noires si le ratio differe). On
    passe par une cible hors-ecran a la resolution du jeu : ainsi tout le code
    de dessin (et les cameras) continue de raisonner en 1408 x 792, quelle que
    soit la taille reelle de l'ecran.
    """

    def __init__(self, plein_ecran: bool = True):
        super().__init__(
            C.LARGEUR_FENETRE, C.HAUTEUR_FENETRE, C.TITRE_FENETRE,
            update_rate=1 / C.IMAGES_PAR_SECONDE,
            fullscreen=plein_ecran, vsync=True, resizable=True,
        )
        self._mise_a_echelle = False
        try:
            texture = self.ctx.texture(
                (C.LARGEUR_FENETRE, C.HAUTEUR_FENETRE),
                filter=(arcade.gl.LINEAR, arcade.gl.LINEAR))
            self._cible = self.ctx.framebuffer(color_attachments=[texture])
            self._camera_jeu = arcade.Camera2D(
                viewport=arcade.LBWH(0, 0, C.LARGEUR_FENETRE, C.HAUTEUR_FENETRE))
            self._programme = self.ctx.utility_textured_quad_program
            self._quad = geometry.quad_2d_fs()   # recalcule au 1er rendu
            self._taille_quad = None
            self._mise_a_echelle = True
        except Exception as e:                       # secours : rendu direct
            print(f"[plein ecran] mise a l'echelle indisponible : {e}")

    def _maj_quad(self):
        """Le quad de sortie garde le ratio 1408:792 (bandes noires sinon).

        Recalcule seulement quand la taille du framebuffer change (rare) :
        robuste au passage plein ecran / fenetre et au retina.
        """
        sw, sh = self.get_framebuffer_size()
        if self._taille_quad == (sw, sh) or sw <= 0 or sh <= 0:
            return
        self._taille_quad = (sw, sh)
        ech = min(sw / C.LARGEUR_FENETRE, sh / C.HAUTEUR_FENETRE)
        ndc_w = (C.LARGEUR_FENETRE * ech / sw) * 2.0
        ndc_h = (C.HAUTEUR_FENETRE * ech / sh) * 2.0
        self._quad = geometry.quad_2d(size=(ndc_w, ndc_h))

    def on_key_press(self, symbole: int, modificateurs: int):
        if symbole == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

    # -- souris : ramener les coordonnees ecran dans l'espace 1408 x 792 ----
    _EVENEMENTS_SOURIS = frozenset((
        "on_mouse_motion", "on_mouse_press", "on_mouse_release",
        "on_mouse_drag", "on_mouse_scroll"))

    def dispatch_event(self, nom, *args):
        if (getattr(self, "_mise_a_echelle", False)
                and nom in self._EVENEMENTS_SOURIS and len(args) >= 2):
            args = self._souris_logique(nom, args)
        return super().dispatch_event(nom, *args)

    def _souris_logique(self, nom, args):
        larg, haut = self.get_size()
        ech = min(larg / C.LARGEUR_FENETRE, haut / C.HAUTEUR_FENETRE) or 1
        ox = (larg - C.LARGEUR_FENETRE * ech) / 2
        oy = (haut - C.HAUTEUR_FENETRE * ech) / 2
        x = (args[0] - ox) / ech
        y = (args[1] - oy) / ech
        reste = list(args[2:])
        if nom in ("on_mouse_motion", "on_mouse_drag") and len(args) >= 4:
            reste[0] = args[2] / ech          # dx
            reste[1] = args[3] / ech          # dy
        return (x, y, *reste)

    # -- rendu : le jeu dans la cible, puis la cible mise a l'echelle -------
    def draw(self, delta_time: float) -> None:
        if not self._mise_a_echelle:
            return super().draw(delta_time)
        self.switch_to()
        # 1. on rend le jeu dans la cible logique 1408 x 792
        self._cible.use()
        self._cible.clear(color=self.background_color)
        self._camera_jeu.use()
        self.dispatch_event("on_draw")
        self.dispatch_event("on_refresh", delta_time)
        # 2. on etire la cible sur l'ecran (centree, bandes noires), fond noir
        self.ctx.screen.use()
        self.ctx.screen.clear(color=(0, 0, 0))
        self._maj_quad()
        self._cible.color_attachments[0].use(0)
        self._quad.render(self._programme)
        self.flip()


def main() -> None:
    args = sys.argv[1:]
    plein_ecran = "fenetre" not in args
    niveau = next((int(a) for a in args if a.isdigit()), None)

    fenetre = FenetreJeu(plein_ecran=plein_ecran)

    if niveau is not None:
        fenetre.show_view(VueJeu(niveau))
    else:
        from views.menu import MenuView
        fenetre.show_view(MenuView())

    arcade.run()


if __name__ == "__main__":
    main()

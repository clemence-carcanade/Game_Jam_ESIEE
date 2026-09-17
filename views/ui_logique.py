"""Un UIManager qui vit dans l'espace logique du jeu (1408 x 792).

En plein ecran, la fenetre dessine tout dans une cible logique remise a
l'echelle de l'ecran, et les evenements souris arrivent deja convertis dans
cet espace (voir FenetreJeu dans main.py). Mais le UIManager d'arcade se cale
sur la taille reelle de la fenetre : le menu partait vers la droite et le
survol / les clics ne tombaient plus sous le curseur patte. On force donc ici
sa mise en page, son rendu et sa conversion souris a raisonner en 1408 x 792.
"""

import arcade
import arcade.gui
from arcade.gui.surface import Surface

from game import constantes as C

RECT_LOGIQUE = arcade.LBWH(0, 0, C.LARGEUR_FENETRE, C.HAUTEUR_FENETRE)


class UIManagerLogique(arcade.gui.UIManager):
    def __init__(self, window=None):
        super().__init__(window)
        # Sert au dessin final ET a convertir les coordonnees souris
        # (adjust_mouse_coordinates) : projection logique, pas la fenetre.
        self.camera = arcade.Camera2D(viewport=RECT_LOGIQUE)

    @property
    def rect(self) -> arcade.types.Rect:
        # La taille annoncee aux layouts (UIAnchorLayout, size_hint...).
        return RECT_LOGIQUE

    def _get_surface(self, layer: int) -> Surface:
        # Comme la version d'arcade, mais les surfaces font la taille logique :
        # c'est sur leur taille que se calcule la mise en page.
        if layer not in self._surfaces:
            if len(self._surfaces) > 2:
                raise Exception("Don't use too much layers!")
            self._surfaces[layer] = Surface(
                size=(C.LARGEUR_FENETRE, C.HAUTEUR_FENETRE),
                pixel_ratio=self.window.get_pixel_ratio(),
            )
            self._surfaces[layer]._pixelated = self._pixelated
        return self._surfaces[layer]

    def on_resize(self, width, height):
        # La fenetre change (F11, autre ecran), pas l'espace logique : on ne
        # suit que le pixel_ratio, et on garde nos cameras logiques.
        ratio = self.window.get_pixel_ratio()
        for surface in self._surfaces.values():
            surface.resize(
                size=(C.LARGEUR_FENETRE, C.HAUTEUR_FENETRE), pixel_ratio=ratio)
        self.trigger_render()

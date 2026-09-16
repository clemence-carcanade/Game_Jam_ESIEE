"""Les petits effets qui donnent du peps : particules et secousse d'ecran.

Rien de complique. Un chat qui grille une vie fait un "pouf" d'etoiles (droit
du brief), l'ecran tremble un court instant, et le chat s'etire quand il saute,
s'aplatit quand il retombe. Ce sont ces details qui rendent un jeu vivant.
"""

import math
import random

import arcade

from game import constantes as C


class Etoile:
    """Une etoile du pouf : elle jaillit, ralentit, tourne et s'efface."""

    def __init__(self, x, y, couleur):
        angle = random.uniform(0, math.tau)
        vitesse = random.uniform(3, 8)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * vitesse
        self.vy = math.sin(angle) * vitesse + 3     # un peu vers le haut
        self.vie = 1.0
        self.taille = random.uniform(4, 9)
        self.rotation = random.uniform(0, 360)
        self.couleur = couleur

    def vivant(self):
        return self.vie > 0

    def mettre_a_jour(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.vy -= 0.4                              # une gravite douce
        self.vx *= 0.92
        self.rotation += 8
        self.vie -= dt * 1.6


class CroixSoin:
    """Une petite croix verte de soin : elle monte doucement et s'efface."""

    def __init__(self, x, y):
        self.x = x + random.uniform(-16, 16)
        self.y = y + random.uniform(-12, 12)
        self.vy = random.uniform(1.2, 2.6)
        self.vie = 1.0
        self.taille = random.uniform(5, 9)

    def vivant(self):
        return self.vie > 0

    def mettre_a_jour(self, dt):
        self.y += self.vy
        self.vy *= 0.98
        self.vie -= dt * 1.1


class Effets:
    """Regroupe les particules et la secousse d'ecran d'une partie."""

    def __init__(self):
        self.etoiles = []
        self.croix = []
        self.secousse = 0.0

    # -- declencheurs ---------------------------------------------------
    def pouf(self, x, y, couleur=(255, 224, 120), nombre=16):
        """Le petit pouf d'etoiles, la ou le chat vient de changer de vie."""
        for _ in range(nombre):
            self.etoiles.append(Etoile(x, y, couleur))

    def soin(self, x, y, nombre=10):
        """Des petites croix vertes qui montent : le medecin te soigne."""
        for _ in range(nombre):
            self.croix.append(CroixSoin(x, y))

    def trembler(self, force=10.0):
        self.secousse = force

    # -- boucle ---------------------------------------------------------
    def mettre_a_jour(self, dt):
        self.etoiles = [e for e in self.etoiles if e.vivant()]
        for e in self.etoiles:
            e.mettre_a_jour(dt)
        self.croix = [c for c in self.croix if c.vivant()]
        for c in self.croix:
            c.mettre_a_jour(dt)
        self.secousse = max(0.0, self.secousse - dt * 60)

    def decalage(self):
        """Le petit tremblement a appliquer au dessin, puis a annuler."""
        if self.secousse <= 0:
            return 0.0, 0.0
        return (random.uniform(-1, 1) * self.secousse,
                random.uniform(-1, 1) * self.secousse)

    def dessiner(self):
        # les croix vertes de soin (deux barres croisees)
        for c in self.croix:
            a = max(0, min(255, int(255 * c.vie)))
            vert = (90, 220, 120, a)
            r = c.taille
            e = r * 0.36
            arcade.draw_lrbt_rectangle_filled(c.x - e, c.x + e, c.y - r, c.y + r, vert)
            arcade.draw_lrbt_rectangle_filled(c.x - r, c.x + r, c.y - e, c.y + e, vert)
        for e in self.etoiles:
            alpha = max(0, min(255, int(255 * e.vie)))
            c = (*e.couleur, alpha)
            # une etoile a quatre branches, faite de deux losanges croises
            r = e.taille
            for da in (0, 90):
                a = math.radians(e.rotation + da)
                dx, dy = math.cos(a) * r, math.sin(a) * r
                px, py = math.cos(a + 1.57) * r * 0.4, math.sin(a + 1.57) * r * 0.4
                arcade.draw_polygon_filled(
                    [(e.x + dx, e.y + dy), (e.x + px, e.y + py),
                     (e.x - dx, e.y - dy), (e.x - px, e.y - py)], c)

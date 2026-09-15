"""La vie de fond : ce qui bouge tout seul pour que la maison respire.

Tout est procedural, sans nouvel asset : des poussieres dorees qui flottent, les
lampes qui respirent, la tele qui scintille, et des petits PNJ (un chat qui
deambule, un papillon qui vole). Ca ne change rien au gameplay, juste au ressenti.
"""

import math
import random

import arcade

from game import constantes as C
from game import maison


class Poussiere:
    """Un grain de lumiere qui derive lentement vers le haut."""

    def __init__(self, largeur, hauteur):
        self.x = random.uniform(0, largeur)
        self.y = random.uniform(0, hauteur)
        self.vx = random.uniform(-0.2, 0.2)
        self.vy = random.uniform(0.15, 0.5)
        self.taille = random.uniform(1.2, 2.6)
        self.phase = random.uniform(0, math.tau)
        self.h = hauteur

    def mettre_a_jour(self, dt, t):
        self.x += self.vx + math.sin(t + self.phase) * 0.15
        self.y += self.vy
        if self.y > self.h + 5:
            self.y = -5
            self.x += random.uniform(-40, 40)


class Ambiance:
    """Rassemble tout ce qui bouge en fond dans un niveau."""

    def __init__(self, niveau):
        self.t = 0.0
        self.largeur = C.LARGEUR_FENETRE
        self.hauteur = C.HAUTEUR_FENETRE
        self.point = niveau.point
        self.poussieres = [Poussiere(self.largeur, self.hauteur) for _ in range(70)]
        self.lampes = [self.point(pos) for pos in maison.LAMPES]
        self.ecrans = [self.point(pos) for pos in maison.ECRANS]

        # les PNJ qui deambulent : un petit sprite qui fait l'aller-retour
        self.promeneurs = []
        for xg, xd, ysol in maison.PROMENADES:
            gx, gy = self.point((xg, ysol))
            dx, _ = self.point((xd, ysol))
            self.promeneurs.append(dict(
                x=gx, y=gy, min=gx, max=dx,
                vx=random.choice((-1, 1)) * 0.7, sens=1,
            ))
        self.papillons = []
        for x, y, r in maison.PAPILLONS:
            cx, cy = self.point((x, y))
            self.papillons.append(dict(cx=cx, cy=cy, r=r * (self.largeur / maison.LARGEUR_IMAGE),
                                       phase=random.uniform(0, math.tau)))

    def mettre_a_jour(self, dt):
        self.t += dt
        for p in self.poussieres:
            p.mettre_a_jour(dt, self.t)
        for m in self.promeneurs:
            m["x"] += m["vx"]
            if m["x"] < m["min"] or m["x"] > m["max"]:
                m["vx"] *= -1
                m["x"] = max(m["min"], min(m["max"], m["x"]))

    def dessiner(self):
        # 1. les halos des lampes, qui respirent
        for lx, ly in self.lampes:
            pulse = 0.75 + 0.25 * math.sin(self.t * 2)
            for i, r in enumerate((70, 46, 26)):
                a = int((10 + i * 9) * pulse)
                arcade.draw_circle_filled(lx, ly, r, (255, 224, 150, a))
        # 2. la tele qui scintille (bleu qui pulse vite)
        for ex, ey in self.ecrans:
            flick = 0.5 + 0.5 * math.sin(self.t * 11 + math.sin(self.t * 3))
            arcade.draw_circle_filled(ex, ey, 34, (120, 180, 235, int(30 * flick)))
        # 3. les papillons, en vol lent facon huit
        for b in self.papillons:
            bx = b["cx"] + math.cos(self.t * 0.9 + b["phase"]) * b["r"]
            by = b["cy"] + math.sin(self.t * 1.8 + b["phase"]) * b["r"] * 0.5
            bat = 3 + 2 * math.sin(self.t * 14)
            for cote in (-1, 1):
                arcade.draw_circle_filled(bx + cote * bat, by, 3, (240, 190, 90, 220))
            arcade.draw_circle_filled(bx, by, 1.6, (60, 45, 40, 230))
        # 4. les promeneurs (un chat qui deambule) : petite ombre + corps
        for m in self.promeneurs:
            sens = 1 if m["vx"] > 0 else -1
            bob = math.sin(self.t * 6) * 1.5
            arcade.draw_ellipse_filled(m["x"], m["y"] + 1, 26, 6, (0, 0, 0, 60))
            arcade.draw_lbwh_rectangle_filled(m["x"] - 13, m["y"] + 3 + bob, 24, 11, (150, 150, 160))
            arcade.draw_lbwh_rectangle_filled(m["x"] + sens * 9 - 4, m["y"] + 10 + bob, 9, 8, (150, 150, 160))
            arcade.draw_lbwh_rectangle_filled(m["x"] - sens * 13, m["y"] + 5 + bob, 6, 3, (150, 150, 160))
        # 5. les poussieres dorees, par-dessus tout
        for p in self.poussieres:
            scint = 0.5 + 0.5 * math.sin(self.t * 3 + p.phase)
            arcade.draw_circle_filled(p.x, p.y, p.taille, (255, 236, 170, int(120 * scint)))

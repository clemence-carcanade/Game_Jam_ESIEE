"""Le son du jeu, tolerant aux fichiers manquants.

Depose des .wav dans assets/sons/ pour les entendre ; sans eux, le jeu tourne
en silence, sans planter. Fichiers attendus :

    saut, atterrissage, mort, piege, reincarnation, win, ambiance

``ambiance`` tourne en boucle (musique de fond).
"""

import arcade

from game import constantes as C

NOMS = ("saut", "atterrissage", "mort", "piege", "reincarnation", "win")
EXTENSIONS = (".wav", ".ogg", ".mp3")


class Audio:
    def __init__(self):
        self.muet = False
        self._sons = {}
        for nom in NOMS:
            son = self._charger(nom)
            if son is not None:
                self._sons[nom] = son
        self._ambiance = self._charger("ambiance")
        self._lecteur_ambiance = None

    def _charger(self, nom):
        for ext in EXTENSIONS:
            chemin = C.DOSSIER_SONS / f"{nom}{ext}"
            if chemin.is_file():
                try:
                    return arcade.Sound(chemin)
                except Exception as e:
                    print(f"[audio] {chemin.name} illisible : {e}")
        return None

    def jouer(self, nom, volume=0.6):
        if self.muet:
            return
        son = self._sons.get(nom)
        if son is not None:
            arcade.play_sound(son, volume=volume)

    def demarrer_ambiance(self):
        if self._ambiance and not self.muet and self._lecteur_ambiance is None:
            self._lecteur_ambiance = arcade.play_sound(self._ambiance, volume=0.3, loop=True)

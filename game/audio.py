"""Le son du jeu, tolerant aux fichiers manquants.

Depose des .wav dans assets/sons/ pour les entendre ; sans eux, le jeu tourne
en silence, sans planter. Fichiers attendus :

    saut, atterrissage, mort, piege, reincarnation, win, ambiance

``ambiance`` est la musique de fond par defaut (menu, secours). Pour une
musique par niveau, depose ``niveau1`` a ``niveau7`` (n'importe quelle
extension) : elle remplace l'ambiance quand ce niveau se charge. Sans fichier
propre au niveau, on retombe sur ``ambiance``, et sans ``ambiance`` le jeu est
silencieux.
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
        self._musiques = {n: self._charger(f"niveau{n}") for n in range(1, 8)}
        self._lecteur_musique = None
        self._musique_en_cours = None

    def jouer_musique(self, numero):
        """Lance la musique du niveau (ou l'ambiance a defaut), en boucle.

        Ne relance rien si c'est deja la bonne piste qui tourne : on ne coupe
        pas la musique d'un niveau qu'on recommence.
        """
        piste = self._musiques.get(numero) or self._ambiance
        if piste is None or self.muet:
            return
        if piste is self._musique_en_cours and self._lecteur_musique is not None:
            return
        self.arreter_musique()
        self._musique_en_cours = piste
        self._lecteur_musique = arcade.play_sound(piste, volume=0.35, loop=True)

    def arreter_musique(self):
        if self._lecteur_musique is not None:
            try:
                arcade.stop_sound(self._lecteur_musique)
            except Exception:
                pass
            self._lecteur_musique = None
            self._musique_en_cours = None

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
        """Compat : lance l'ambiance par defaut (le menu s'en sert)."""
        if self._ambiance and not self.muet and self._lecteur_musique is None:
            self._musique_en_cours = self._ambiance
            self._lecteur_musique = arcade.play_sound(self._ambiance, volume=0.3, loop=True)

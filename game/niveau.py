"""Lecture d'un niveau depuis ``niveaux/niveau_N.txt``.

Format du fichier (c'est le contrat qui permet à tout le monde de créer du
contenu sans toucher au code) :

* **1re ligne** : les métadonnées, en JSON, sur une seule ligne.

      {"titre": "Chez Léo", "maitre": "leo", "aide": "Les poufs amortissent tout."}

* **lignes suivantes** : la carte, un caractère = une tuile de 64 x 64.
  La première ligne de carte est le **haut** du niveau (on dessine comme on
  lit). L'origine (0, 0) d'arcade reste en bas à gauche.

      .   vide                    O   objet poussable (pouf, caisse, panier)
      #   mur / sol               B   bouton / plaque de pression
      =   plateforme traversable  D   porte (s'ouvre avec le bouton)
      C   départ du chat          1-9 élément scripté propre au niveau
      M   départ du maître        X   élément mortel

Les métadonnées acceptent aussi les réflexes à désactiver au chargement :

      {"titre": "...", "reflexes_coupes": ["moustaches"]}
"""

import json
from dataclasses import dataclass, field

import arcade

from game import constantes as C


def _carre(largeur, hauteur, couleur, x, y, nom):
    """Un rectangle plein, en attendant les vrais sprites."""
    texture = arcade.Texture.create_empty(nom, (int(largeur), int(hauteur)), couleur)
    return arcade.Sprite(texture, center_x=x, center_y=y)


@dataclass
class Niveau:
    """Tout ce qu'un niveau contient, prêt pour le moteur de collisions."""

    titre: str = ""
    maitre: str = ""
    aide: str = ""
    largeur: float = 0.0
    hauteur: float = 0.0
    depart_chat: tuple = (0.0, 0.0)
    depart_maitre: tuple = (0.0, 0.0)
    reflexes_coupes: list = field(default_factory=list)

    murs: arcade.SpriteList = field(default_factory=lambda: arcade.SpriteList(use_spatial_hash=True))
    plateformes: arcade.SpriteList = field(default_factory=lambda: arcade.SpriteList(use_spatial_hash=True))
    mortels: arcade.SpriteList = field(default_factory=lambda: arcade.SpriteList(use_spatial_hash=True))
    poussables: arcade.SpriteList = field(default_factory=arcade.SpriteList)
    zones: arcade.SpriteList = field(default_factory=arcade.SpriteList)
    scriptes: dict = field(default_factory=dict)

    def dessiner(self) -> None:
        self.murs.draw()
        self.plateformes.draw()
        self.zones.draw()
        self.mortels.draw()
        self.poussables.draw()


def chemin_du_niveau(numero: int):
    return C.DOSSIER_NIVEAUX / f"niveau_{numero}.txt"


def charger(numero: int) -> Niveau:
    """Lit ``niveaux/niveau_<numero>.txt`` et construit le niveau."""
    chemin = chemin_du_niveau(numero)
    if not chemin.is_file():
        raise FileNotFoundError(f"Niveau introuvable : {chemin}")

    lignes = chemin.read_text(encoding="utf-8").splitlines()
    if not lignes:
        raise ValueError(f"Niveau vide : {chemin}")

    metadonnees = json.loads(lignes[0])
    carte = [ligne for ligne in lignes[1:] if ligne.strip()]
    return construire(carte, metadonnees)


def construire(carte, metadonnees=None) -> Niveau:
    """Construit un niveau à partir d'une liste de lignes (pratique pour les tests)."""
    metadonnees = metadonnees or {}
    niveau = Niveau(
        titre=metadonnees.get("titre", ""),
        maitre=metadonnees.get("maitre", ""),
        aide=metadonnees.get("aide", ""),
        reflexes_coupes=metadonnees.get("reflexes_coupes", []),
    )

    tuile = C.TAILLE_TUILE
    nb_lignes = len(carte)
    niveau.hauteur = nb_lignes * tuile
    niveau.largeur = max(len(ligne) for ligne in carte) * tuile

    for numero_ligne, ligne in enumerate(carte):
        for colonne, caractere in enumerate(ligne):
            # la 1re ligne du fichier est en haut, l'origine d'arcade est en bas
            x = colonne * tuile + tuile / 2
            y = (nb_lignes - 1 - numero_ligne) * tuile + tuile / 2
            _placer(niveau, caractere, x, y)

    return niveau


def _placer(niveau: Niveau, caractere: str, x: float, y: float) -> None:
    tuile = C.TAILLE_TUILE

    if caractere == C.CAR_MUR:
        niveau.murs.append(_carre(tuile, tuile, C.COULEUR_MUR, x, y, "mur"))

    elif caractere == C.CAR_PLATEFORME:
        # fine et posée en haut de la tuile : on passe dessous sans se cogner
        hauteur = tuile // 4
        niveau.plateformes.append(
            _carre(tuile, hauteur, C.COULEUR_PLATEFORME, x, y + tuile / 2 - hauteur / 2, "plateforme")
        )

    elif caractere == C.CAR_MORTEL:
        hauteur = tuile // 2
        mortel = _carre(tuile, hauteur, C.COULEUR_MORTEL, x, y - tuile / 2 + hauteur / 2, "mortel")
        mortel.cause_de_mort = "les pointes"
        niveau.mortels.append(mortel)

    elif caractere == C.CAR_POUSSABLE:
        objet = _carre(tuile - 8, tuile - 8, C.COULEUR_POUSSABLE, x, y, "poussable")
        objet.amortit = True          # un pouf : il amortit les chutes
        niveau.poussables.append(objet)

    elif caractere == C.CAR_BOUTON:
        hauteur = tuile // 6
        bouton = _carre(tuile, hauteur, C.COULEUR_BOUTON, x, y - tuile / 2 + hauteur / 2, "bouton")
        bouton.role = "bouton"
        niveau.zones.append(bouton)

    elif caractere == C.CAR_PORTE:
        porte = _carre(tuile / 2, tuile, C.COULEUR_PORTE, x, y, "porte")
        porte.role = "porte"
        niveau.murs.append(porte)     # fermée = solide ; jeu.py l'ouvrira

    elif caractere == C.CAR_CHAT:
        niveau.depart_chat = (x, y)

    elif caractere == C.CAR_MAITRE:
        niveau.depart_maitre = (x, y)

    elif caractere in C.CARS_SCRIPTES:
        # laissé au responsable du niveau : il fera ce qu'il veut de ces positions
        niveau.scriptes.setdefault(caractere, []).append((x, y))

"""Lecture d'un niveau depuis ``niveaux/niveau_N.txt``.

Format du fichier (c'est le contrat qui permet à tout le monde de créer du
contenu sans toucher au code) :

* **1re ligne** : les métadonnées, en JSON, sur une seule ligne.

      {"titre": "Chez Léo", "maitre": "leo", "aide": "Les poufs amortissent tout."}

* **lignes suivantes** : la carte, un caractère = une tuile de 64 x 64.
  La première ligne de carte est le **haut** du niveau (on dessine comme on
  lit). L'origine (0, 0) d'arcade reste en bas à gauche.

      .   vide                    O   objet poussable (sac, caisse, pouf)
      #   mur / sol               B   bouton / plaque de pression
      =   plateforme traversable  D   porte (s'ouvre avec le bouton)
      C   départ du chat          1-9 mobilier (voir MOBILIER plus bas)
      M   départ du maître        X   élément mortel

Le mobilier (1 à 9) est décrit dans le dictionnaire ``MOBILIER`` : un nom, une
hauteur en fraction de tuile, une couleur et un comportement. Les couleurs sont
des **placeholders** : quand les tuiles des packs arriveront, il suffira de
remplacer la couleur par une image, le reste du code ne bouge pas.

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


#: mobilier du jeu : caractère -> (nom, hauteur en tuiles, couleur, comportement)
#:
#: Comportements possibles :
#:   "decor"      dessiné, mais on le traverse (télé, plante, tapis, habitants)
#:   "plateforme" traversable par le bas, on peut se poser dessus (canapé)
#:   "mur"        solide de tous les côtés (buffet)
#:   "verre"      plateforme + surface glissante (la table du salon)
#:   "gamelle"    zone : c'est là que le chat peut manger
MOBILIER = {
    "1": ("gamelle", 0.45, C.COULEUR_GAMELLE, "gamelle"),
    "2": ("table_verre", 0.25, C.COULEUR_VERRE, "verre"),
    "3": ("canape", 1.0, C.COULEUR_CANAPE, "plateforme"),
    "4": ("buffet", 1.0, C.COULEUR_BUFFET, "mur"),
    "5": ("television", 0.9, C.COULEUR_TELE, "decor"),
    "6": ("plante", 1.3, C.COULEUR_PLANTE, "decor"),
    "7": ("tapis", 0.12, C.COULEUR_TAPIS, "decor"),
    "8": ("maitresse", 1.2, C.COULEUR_MAITRESSE, "decor"),
    "9": ("rambarde", 0.8, C.COULEUR_RAMBARDE, "decor"),
}


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
    decor: arcade.SpriteList = field(default_factory=arcade.SpriteList)
    scriptes: dict = field(default_factory=dict)

    def dessiner(self) -> None:
        # le décor passe derrière tout le reste : il ne bloque jamais le chat
        self.decor.draw()
        self.murs.draw()
        self.plateformes.draw()
        self.zones.draw()
        self.mortels.draw()
        self.poussables.draw()

    def trouver_zone(self, role: str):
        """Retourne la première zone ayant ce rôle (``gamelle``, ``verre``...)."""
        for zone in self.zones:
            if getattr(zone, "role", "") == role:
                return zone
        return None


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
        # TODO (maitre.py) : remplacer par la vraie classe Maitre
        daron = _carre(tuile, int(tuile * 1.2), C.COULEUR_MAITRE,
                       x, y - tuile / 2 + tuile * 1.2 / 2, "maitre")
        daron.nom = "maitre"
        niveau.decor.append(daron)

    elif caractere in MOBILIER:
        _placer_mobilier(niveau, caractere, x, y)

    elif caractere in C.CARS_SCRIPTES:
        # laissé au responsable du niveau : il fera ce qu'il veut de ces positions
        niveau.scriptes.setdefault(caractere, []).append((x, y))


def _placer_mobilier(niveau: Niveau, caractere: str, x: float, y: float) -> None:
    """Pose un meuble, et le range dans la bonne liste selon son comportement."""
    tuile = C.TAILLE_TUILE
    nom, hauteur_tuiles, couleur, comportement = MOBILIER[caractere]

    hauteur = max(4, int(tuile * hauteur_tuiles))
    # le meuble est posé sur le bas de sa case, comme un vrai meuble sur le sol
    meuble = _carre(tuile, hauteur, couleur, x, y - tuile / 2 + hauteur / 2, nom)
    meuble.nom = nom
    niveau.scriptes.setdefault(caractere, []).append((x, y))

    if comportement == "decor":
        niveau.decor.append(meuble)

    elif comportement == "plateforme":
        niveau.decor.append(meuble)
        # on se pose sur le dessus du meuble, sans se cogner dedans par en bas
        dessus = _carre(tuile, tuile // 4, couleur, x, y + tuile / 2 - tuile / 8, nom + "_dessus")
        niveau.plateformes.append(dessus)

    elif comportement == "mur":
        niveau.murs.append(meuble)

    elif comportement == "verre":
        plateau = _carre(
            tuile, hauteur, couleur, x, y + tuile / 2 - hauteur / 2, nom
        )
        plateau.nom = nom
        niveau.plateformes.append(plateau)
        # la zone glissante déborde d'une tuile vers le haut, sinon le chat
        # posé dessus ne la touche pas (il est *au-dessus* du plateau)
        glisse = _carre(tuile, tuile, (0, 0, 0, 0), x, y + tuile / 2, nom + "_glisse")
        glisse.role = "verre"
        niveau.zones.append(glisse)

    elif comportement == "gamelle":
        meuble.role = "gamelle"
        meuble.remplie = False
        niveau.zones.append(meuble)

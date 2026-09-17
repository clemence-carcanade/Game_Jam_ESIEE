"""Toutes les valeurs réglables du jeu.

Règle d'équipe : aucun nombre "en dur" ailleurs dans le code. Si tu as besoin
d'une valeur, elle se déclare ici et s'importe :

    from game import constantes as C
    ...
    self.change_y = C.VITESSE_SAUT
"""

from pathlib import Path

import arcade

# ---------------------------------------------------------------------------
# Chemins (pathlib : l'équipe est mixte macOS / Windows)
# ---------------------------------------------------------------------------
DOSSIER_RACINE = Path(__file__).resolve().parent.parent
DOSSIER_ASSETS = DOSSIER_RACINE / "assets"
DOSSIER_IMAGES = DOSSIER_ASSETS / "images"
DOSSIER_SONS = DOSSIER_ASSETS / "sons"
DOSSIER_NIVEAUX = DOSSIER_RACINE / "niveaux"

# ---------------------------------------------------------------------------
# Fenêtre
# ---------------------------------------------------------------------------
LARGEUR_FENETRE = 1408   # 22 cases de 64 px
HAUTEUR_FENETRE = 792   # la maison peinte, a l'echelle 1408/1672
TITRE_FENETRE = "Chat Va Mal"
IMAGES_PAR_SECONDE = 60

# ---------------------------------------------------------------------------
# Monde
# ---------------------------------------------------------------------------
TAILLE_TUILE = 64          # une tuile = 64 x 64 pixels
VIES_DEPART = 7
NOMBRE_NIVEAUX = 6             # 6 foyers ; apres le 6e, la video de fin puis le menu

# ---------------------------------------------------------------------------
# Physique du chat (valeurs par image, comme le moteur d'arcade)
# ---------------------------------------------------------------------------
GRAVITE = 1.0
LARGEUR_CHAT = 48              # taille du carré de secours, sans les sprites
HAUTEUR_CHAT = 48
ECHELLE_CHAT = 4.0             # meme monde que les meubles : un chat = une case
VITESSE_CHAT = 6.0             # vitesse horizontale maximale
ACCELERATION_SOL = 1.2
ACCELERATION_AIR = 0.7         # on contrôle moins bien le chat en l'air
FREINAGE = 1.5
VITESSE_SAUT = 18.0            # ~2,5 tuiles de haut
VITESSE_CHUTE_MAX = 25.0
TEMPS_COYOTE = 0.10            # on peut encore sauter 0,1 s après le bord
MEMOIRE_SAUT = 0.12            # un saut demandé trop tôt est mémorisé
COUPURE_SAUT = 0.45            # relâcher la touche raccourcit le saut

# ---------------------------------------------------------------------------
# Surfaces glissantes (la fameuse table "en verre" du salon)
# ---------------------------------------------------------------------------
GLISSE_FREINAGE = 0.06         # le chat ne freine presque plus
GLISSE_ACCELERATION = 0.35     # et il a du mal a repartir

# ---------------------------------------------------------------------------
# Faux piege : la tete coincee dans le sac de croquettes
# ---------------------------------------------------------------------------
DUREE_DANS_LE_SAC = 2.5        # secondes a foncer droit devant sans rien voir

# ---------------------------------------------------------------------------
# Mini-jeu des piments (niveau 5) : vider sa barre de vie en mangeant vite
# ---------------------------------------------------------------------------
VIE_MAX = 100.0
PIMENT_DEGATS = 16.0          # ce qu'un piment retire a la barre de vie
VIE_REGEN = 12.0             # ce que la barre remonte par seconde (difficulte)
PIMENT_RESPAWN = 1.6         # secondes avant qu'un piment mange reapparaisse

# ---------------------------------------------------------------------------
# Niveau 1 : l escalade jusqu au distributeur de chocolat (se gaver a mort)
# ---------------------------------------------------------------------------
SATIETE_MAX = 100.0
CROQUETTE_GAVE = 6.0         # ce qu une tablette ramassee ajoute a la satiete
DISTRIBUTEUR_GAVE = 48.0     # ce que le distributeur deverse par seconde au contact
SATIETE_DIGESTION = 0.0      # ce que la satiete redescend par seconde (0 = niveau facile)

# Niveau 1 en mode Doodle Jump (scroller vertical, rebond automatique)
REBOND_DOODLE = 19.0          # vitesse verticale rendue a chaque atterrissage
DOODLE_NB_PLATEFORMES = 32    # hauteur de la tour a grimper
DOODLE_ESPACE_MIN = 85        # ecart vertical mini entre deux etageres
DOODLE_ESPACE_MAX = 120       # ... et maxi (doit rester sous la hauteur de rebond)

# ---------------------------------------------------------------------------
# Chutes
# ---------------------------------------------------------------------------
# Un chat retombe sur ses pattes : tant que le réflexe est actif, il encaisse
# des chutes bien plus hautes. Tout le niveau 1 consiste à dépasser ce seuil.
# Avec le reflexe des pattes, aucune chute ne tue : il faut couper le reflexe.
CHUTE_MORTELLE = 3 * TAILLE_TUILE              # une fois le reflexe coupe
MARGE_HORS_NIVEAU = 200        # tombé plus bas que ça = sorti du niveau

# ---------------------------------------------------------------------------
# Objets poussables (poufs, caisses, paniers)
# ---------------------------------------------------------------------------
VITESSE_POUSSEE = 3.0          # un objet se pousse moins vite qu'on ne court
PILE_POUSSABLE_MAX = 6         # nombre d'objets qu'on peut pousser d'un coup

# ---------------------------------------------------------------------------
# Caractères des fichiers de niveau (niveaux/niveau_N.txt)
# ---------------------------------------------------------------------------
CAR_VIDE = "."
CAR_MUR = "#"
CAR_PLATEFORME = "="       # traversable par le bas
CAR_CHAT = "C"
CAR_MAITRE = "M"
CAR_MORTEL = "X"
CAR_POUSSABLE = "O"
CAR_BOUTON = "B"
CAR_PORTE = "D"
CARS_SCRIPTES = "123456789"

# ---------------------------------------------------------------------------
# Couleurs (en attendant les sprites : tout est un rectangle de couleur)
# ---------------------------------------------------------------------------
COULEUR_FOND = (28, 26, 34)
COULEUR_MUR = (92, 84, 104)
COULEUR_PLATEFORME = (140, 120, 90)
COULEUR_CHAT = arcade.color.ORANGE
COULEUR_MAITRE = (120, 160, 220)
COULEUR_MORTEL = (220, 70, 70)
COULEUR_POUSSABLE = (200, 170, 120)
COULEUR_BOUTON = (120, 200, 140)
COULEUR_PORTE = (160, 140, 200)
# Mobilier du salon (placeholders : remplacer par les tuiles des packs)
COULEUR_CANAPE = (150, 80, 90)
COULEUR_BUFFET = (120, 85, 55)
COULEUR_TELE = (45, 45, 60)
COULEUR_PLANTE = (70, 140, 80)
COULEUR_TAPIS = (140, 100, 130)
COULEUR_VERRE = (150, 205, 225)
COULEUR_GAMELLE = (215, 175, 90)
COULEUR_MAITRESSE = (205, 130, 165)
COULEUR_RAMBARDE = (110, 110, 125)

COULEUR_TEXTE = arcade.color.WHITE
COULEUR_TEXTE_FADE = (150, 150, 160)

# ---------------------------------------------------------------------------
# Commandes (AZERTY, flèches en secours)
# ---------------------------------------------------------------------------
TOUCHES_GAUCHE = (arcade.key.Q, arcade.key.LEFT)
TOUCHES_DROITE = (arcade.key.D, arcade.key.RIGHT)
TOUCHES_BAS = (arcade.key.S, arcade.key.DOWN)
TOUCHES_SAUT = (arcade.key.SPACE, arcade.key.Z, arcade.key.UP)
TOUCHES_ACTION = (arcade.key.E,)
TOUCHES_RECOMMENCER = (arcade.key.R,)
TOUCHES_PAUSE = (arcade.key.ESCAPE, arcade.key.P)
TOUCHES_DEBUG = (arcade.key.F1,)

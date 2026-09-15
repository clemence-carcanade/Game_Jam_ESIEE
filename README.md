# Sept Vies

Un chat n'aime pas son maître. Il lui reste sept vies, et il compte bien les
dépenser pour se réincarner ailleurs, jusqu'à trouver le maître idéal.

**Le but de chaque niveau est de faire mourir le chat.** Il n'y a pas de sortie :
il faut atteindre le danger. Sauf que tout s'y oppose — le maître protège le chat
(sols capitonnés, fenêtres condamnées), et le chat se protège tout seul
(il retombe sur ses pattes, ses moustaches lui font esquiver, il s'agrippe aux
rebords). Le puzzle consiste à battre le maître **et** à battre le chat.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## Lancer

```bash
python main.py          # niveau 1
python main.py 2        # directement le niveau 2
python tests/test_collisions.py   # tests du moteur de collisions
```

## Commandes

| Touche | Action |
|---|---|
| `Q` / `D` (ou les flèches) | se déplacer |
| `ESPACE` ou `Z` | sauter (relâcher tôt = saut plus court) |
| `S` | descendre à travers une plateforme `=` |
| `R` | recommencer le niveau |
| `F1` | afficher les boîtes de collision |
| `ÉCHAP` | quitter |

## Architecture

```
main.py                 point d'entrée, ouvre la fenêtre
game/
  constantes.py         toutes les valeurs réglables (aucun nombre en dur ailleurs)
  collisions.py         LE moteur de collisions (voir plus bas)
  chat.py               le joueur : déplacement, saut, réflexes, cicatrices
  niveau.py             lecture des fichiers niveaux/niveau_N.txt
  jeu.py                la vue principale : boucle, dessin, clavier
niveaux/niveau_N.txt    les niveaux, un caractère = une tuile de 64 x 64
assets/images/, sons/   les médias
tests/test_collisions.py  25 tests du moteur, sans ouvrir de fenêtre
```

## Attention : deux architectures coexistent

La branche `dev` contient aujourd'hui **deux organisations de fichiers** :

| | |
|---|---|
| `game/` + `niveaux/` | le moteur, l'architecture du brief Sept Vies |
| `settings.py` + `views/` + `entities/` | le menu et l'ossature poussés en parallèle |

Rien n'a été supprimé, et ça tourne : `main.py` ouvre le menu de `views/menu.py`,
et `ENTRÉE` lance `game.jeu.VueJeu`. Mais il y a deux fichiers de constantes
(`settings.py` et `game/constantes.py`) et deux dossiers pour les vues.

**L'équipe doit trancher, vite.** Le plus simple est de déplacer `views/menu.py`
en `game/ui.py` et de supprimer `settings.py` au profit de `game/constantes.py`,
comme prévu par le brief. Tant que ce n'est pas fait, la taille de la fenêtre
est définie dans `game/constantes.py` et recopiée dans `settings.py` : si l'une
change, changer l'autre.

## Le moteur de collisions

Tout ce qui se touche passe par `game/collisions.py`. Il ne connaît que des
`arcade.SpriteList`, donc il ne bougera pas quand les vrais sprites arriveront.

| Famille | Comportement |
|---|---|
| `murs` (`#`) | solides, jamais traversés |
| `plateformes` (`=`) | traversables par le bas et par les côtés ; on ne peut qu'atterrir dessus, `S` fait redescendre |
| `mortels` (`X`) | font griller une vie au chat |
| `poussables` (`O`) | poufs et caisses : ça se pousse (jusqu'à 6 d'un coup), ça tombe, ça amortit les chutes |
| `zones` (`B`, `D`) | boutons et déclencheurs : détectés sans bloquer le passage |

Il applique aussi les trois **réflexes du chat**, qui sont de simples booléens
que les niveaux doivent désactiver :

| Réflexe | Effet | Comment le niveau doit le battre |
|---|---|---|
| `reflexe_pattes` | **aucune chute ne le tue** (3 tuiles suffisent une fois le réflexe coupé) | étourdir le chat |
| `reflexe_moustaches` | esquive ce qui est mortel au lieu de mourir | couper les moustaches |
| `reflexe_agrippe` | impossible de tomber en marchant : il s'accroche au rebord | scotcher ses pattes (pour tomber, il faut sauter) |

Utilisation, dans une boucle de jeu — **l'ordre compte** :

```python
au_sol = moteur.est_au_sol()               # 1. le chat sait s'il peut sauter
chat.calculer_deplacement(delta_time, au_sol)  # 2. il calcule ses vitesses
contacts = moteur.mettre_a_jour()          # 3. on déplace et on résout tout
if not contacts.vivant:
    jeu.griller_une_vie(contacts.mort)
```

`contacts` dit tout ce qui s'est passé pendant l'image : `au_sol`,
`atterrissage`, `hauteur_chute`, `sur_plateforme`, `esquive`, `mortels`,
`zones`, `hors_niveau`, `mort`. **La mort est signalée sur l'image où elle
arrive**, pas sur les suivantes : il faut la traiter tout de suite.

## Les sprites du chat

`assets/images/chat.png` est la planche du pack *Cat 50+ animations* : une
grille de 8 colonnes sur 51 lignes, cases de 32 x 32 (259 images). Le
découpage est dans `game/animations.py`.

| Animation | Ligne de la planche | Quand |
|---|---|---|
| `repos` | 2 | le chat ne bouge pas |
| `marche` | 17 | il se déplace |
| `saut` | 46 (fin) | il monte |
| `chute` | 47 (début) | il descend |
| `reception` | 47 | il vient de toucher le sol |
| `allonge` | 32 | il vient de griller une vie |
| `reincarnation` | 37 | l'esprit s'élève, le chat se reforme |

Pour ajouter une animation, une ligne suffit dans le dictionnaire
`ANIMATIONS` : `(ligne, première image, nombre d'images, durée d'une image,
en boucle ou non)`. Les lignes 34 à 36 de la planche contiennent des pixels
rouges : on ne les utilise pas, le registre du jeu est cartoon.

Deux points à ne pas casser :

- **La boîte de collision ne dépend pas de l'image.** Le chat n'occupe qu'un
  petit rectangle en bas de sa case de 32 x 32 ; `animations.boite_du_chat()`
  mesure ce rectangle et `Chat.definir_boite_de_collision()` cale la boîte
  dessus. Sans ça le chat flotterait au-dessus du sol et mourrait à cause d'un
  pixel transparent.
- Le chat est dessiné tourné **vers la droite** ; les images sont retournées
  automatiquement quand il va à gauche.
- Taille à l'écran : `ECHELLE_CHAT` dans `constantes.py` (2.5 = un chat
  d'environ 50 x 35 px sur des tuiles de 64).

Si `assets/images/chat.png` est absent, le chat redevient un carré orange et
le jeu tourne quand même.

## Le niveau 1 : le salon

> 20h. Les mêmes croquettes que tous les soirs, le daron devant son match, la
> maîtresse qui commente. Le chat en a assez.

Trois **faux pièges**, qui ont l'air mortels et ne le sont pas — c'est la règle
n°1 : si la mort était évidente, le joueur gagnerait sans réfléchir.

| Faux piège | Ce qui se passe |
|---|---|
| sauter du balcon | le chat retombe sur ses pattes, toujours |
| la table « en verre » | ce n'est qu'un film plastique : ça glisse, ça ne casse pas |
| la tête dans le sac de croquettes | il fonce droit devant, percute un mur, se dégage |

Un seul **vrai piège** : manger les croquettes du fond du sac, celles qui
sentent. Encore faut-il les faire tomber dans la gamelle.

La solution, en trois actions : monter sur le canapé puis sur la table, sauter
sur le buffet, pousser le sac — il se renverse dans la gamelle — puis redescendre
et appuyer sur `E` devant la gamelle.

Le sol du salon est volontairement continu d'un mur à l'autre : un sac poussé du
mauvais côté retombe toujours par terre et reste récupérable. **Aucune situation
ne bloque le niveau** — ne pas casser ça en ajoutant du mobilier posé au sol.

## Le mobilier des niveaux

Les caractères `1` à `9` sont du mobilier, décrit dans `MOBILIER`
(`game/niveau.py`). Chaque meuble a un comportement :

| | Meuble | Comportement |
|---|---|---|
| `1` | gamelle | zone où le chat peut manger (`E`) |
| `2` | table « en verre » | plateforme + **surface glissante** |
| `3` | canapé | plateforme : on monte dessus |
| `4` | buffet | solide de tous les côtés |
| `5` | télévision | décor, on le traverse |
| `6` | plante | décor |
| `7` | tapis | décor |
| `8` | la maîtresse | décor |
| `9` | rambarde du balcon | décor |

Pour ajouter un meuble : une ligne dans `MOBILIER`, avec sa hauteur en fraction
de tuile, sa couleur et son comportement (`decor`, `plateforme`, `mur`, `verre`,
`gamelle`). Le décor est dessiné **derrière** tout le reste et ne bloque jamais
le chat.

## Format des niveaux

`niveaux/niveau_N.txt` — première ligne les métadonnées en JSON, puis la carte.
La première ligne de carte est le **haut** du niveau (on dessine comme on lit).

```
{"titre": "Chez Leo, 6 ans", "maitre": "leo", "aide": "...", "reflexes_coupes": ["moustaches"]}
####################
#..................#
#..........C.M.....#
...
```

| | | | |
|---|---|---|---|
| `.` vide | `#` mur / sol | `=` plateforme traversable | `C` départ du chat |
| `M` départ du maître | `X` élément mortel | `O` objet poussable | `B` bouton |
| `D` porte | `1-9` élément scripté du niveau | | |

`reflexes_coupes` désactive un réflexe dès le chargement : `"pattes"`,
`"moustaches"`, `"agrippe"`.

Deux règles de level design à ne jamais oublier :

1. **La mort évidente doit être impossible**, sinon le joueur marche dans le
   premier piège et gagne. Pas de trou dans le sol, pas de pic accessible.
2. **Toute zone où le chat peut tomber doit être capitonnée**, sauf après
   résolution du puzzle.

## Ce qui n'est pas encore fait

Cette branche livre le moteur (fenêtre, gravité, saut, collisions, mort) et un
niveau 1 de démonstration. Restent à écrire, par leurs responsables :

- `maitre.py` — l'IA des maîtres (détecter → rejoindre → sauver)
- `vies.py` — compteur de vies, cicatrices, progression entre niveaux
- `ui.py` — HUD (7 empreintes de pattes), menus, écrans de transition
- `niveaux/niveau_2.txt` à `niveau_7.txt`
- une caméra, si un niveau dépasse un écran (aujourd'hui : 20 x 11 tuiles)
- **les sprites du décor** : tout le mobilier est encore un rectangle de
  couleur. Les packs repérés (Pet Virtual Mobile, Cat Room, PixelInterior
  LivingRoom/Kitchen, House Interior 32x32, Top-Down Modern City) doivent être
  téléchargés à la main depuis itch.io, puis déposés dans `assets/images/`.
  Ensuite, seul `MOBILIER` est à changer : remplacer la couleur par une texture,
  le reste du code ne bouge pas.

`niveaux/niveau_1.txt` est une carte de démonstration : elle sert à valider le
moteur, elle n'a pas encore été jouée par un humain.

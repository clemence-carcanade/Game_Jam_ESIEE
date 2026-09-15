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

## Le décor

Deux sources, dans cet ordre de priorité :

| Dossier | Contenu | Versionné ? |
|---|---|---|
| `assets/images/packs/` | les meubles découpés dans les packs achetés | **non** |
| `assets/images/decor/` | le décor dessiné en code, qui sert de secours | oui |

```bash
python outils/importe_packs.py     # découpe les packs -> assets/images/packs/
python outils/dessine_decor.py     # redessine le secours -> assets/images/decor/
```

**Les images des packs sont versionnées**, décision de l'équipe : le jeu n'est
pas vendu et personne ne veut télécharger cinq packs avant de pouvoir lancer le
projet. À savoir quand même : les licences de Bitglow et de nacl1234 interdisent
la redistribution de leurs fichiers, et le dépôt est public. Si le projet devait
être diffusé ailleurs qu'en soutenance, il faudrait soit passer le dépôt en
privé, soit retirer `assets/images/packs/` et laisser `importe_packs.py` faire le
travail chez chacun.

Une tuile du pack fait 16 px et s'affiche x4 ; une tuile dessinée fait 32 px et
s'affiche x2. Dans les deux cas, **une tuile = une case du jeu**, et chaque
image garde son échelle (`_echelle()` dans `niveau.py`).

Le décor dessiné en secours vit dans `outils/dessine_decor.py`.

```bash
python outils/dessine_decor.py     # réécrit assets/images/decor/*.png
```

Tuiles de 32 x 32 pixels affichées x2 dans le jeu, même taille de pixel que le
chat, palette limitée en haut du script. Pour changer la couleur du canapé ou la
forme de la télé : une ligne dans le script, puis on relance. Aucun logiciel de
dessin nécessaire, et les diffs restent lisibles.

**Pourquoi pas les packs itch.io ?** Parce que le dépôt est public, et que leurs
licences l'interdisent explicitement — Bitglow : *« You may NOT redistribute the
assets as standalone files »* ; nacl1234 : *« Not permitted: make the original or
lightly modified source files available for download »*. Ces packs ont servi de
**référence visuelle** (leur palette, leurs proportions), ce qui est libre. Si
l'équipe veut vraiment les utiliser tels quels, il faut passer le dépôt en privé
et les garder hors de Git.

Deux mécanismes automatiques dans `game/niveau.py` :

- **les morceaux de meubles.** Trois cases `333` deviennent `canape_g`,
  `canape_m`, `canape_d` ; un meuble sur deux rangées utilise en plus
  `etagere_haut_*` et `etagere_bas_*`. Rien à écrire dans le fichier de niveau.
- **les murs.** Une case `#` prend la texture `sol` si le dessus est vide,
  `plafond` si le dessous est vide, `mur` sinon.

Deux pièges à connaître si tu ajoutes des images :

- **L'image et la collision sont séparées.** L'image va dans `decor`, la forme
  de collision est un rectangle invisible posé à côté. Sans ça, les pieds de la
  table en verre bloqueraient le chat alors que seul le plateau compte.
- **On positionne par l'image, jamais par `sprite.bottom`.** Arcade aligne
  alors la boîte de collision, qui ignore les pixels transparents : une image à
  moitié vide se retrouve décalée.

Si un PNG manque, le meuble redevient un rectangle de couleur et le jeu tourne
quand même.

## Les sept niveaux

Ils vivent dans `game/les_niveaux.py`, produit et verifie par un script —
plus de fichiers `.txt` :

```bash
python outils/genere_niveaux.py     # reecrit game/les_niveaux.py
```

Un niveau y porte sa carte, ses textes **et ses faux pieges scriptes** : une
lettre minuscule sur la carte, un effet a cote. Cinq effets existent :
`message` (il ne se passe rien de grave, et on le dit), `projection` (lance,
pousse — il retombe sur ses pattes), `soin` (quelqu'un le sauve, retour au
depart), `deguisement` (humilie, colore, vivant), `sac` (la tete coincee).
Declenchement `action` (touche E) ou `contact` (marcher dessus).

Chaque niveau a **sa propre geometrie** : le chemin qui monte n'est jamais au
meme endroit (a gauche, en puits, en zigzag, de droite a gauche) et le piege
change de place. Un niveau se decrit en une entree du tableau `NIVEAUX` :
son contexte, ses marches, ses meubles, ou tombe l'objet et ou est le piege.

Le script **verifie** avant d'ecrire, et refuse d'ecrire un niveau casse :

* chaque meuble forme un rectangle plein, sinon il est dessine plusieurs fois ;
* chaque saut du parcours tient dans les capacites du chat (2 cases de haut,
  3 de large) ;
* la colonne ou tombe l'objet est degagee jusqu'au sol, et le piege est dessous.

Mourir fait passer au foyer suivant : c'est l'objectif, pas l'echec. Au
septieme, le jeu s'inverse — le chat est enfin heureux, mourir ne coute plus de
vie mais fait recommencer, et il faut rejoindre la famille vivant (`G`). Les
textes de chaque foyer sont dans les metadonnees du fichier, pas dans le code :
`aide`, `message_piege`, `message_mort`, et `survivre` pour le dernier.

## Format des niveaux

Dans `outils/genere_niveaux.py` — les cartes ASCII restent le format, mais en Python.
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
- les sprites des niveaux 2 à 7 (le décor du salon, lui, est fait)

`niveaux/niveau_1.txt` est une carte de démonstration : elle sert à valider le
moteur, elle n'a pas encore été jouée par un humain.

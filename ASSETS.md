# Assets à trouver — Sept Vies

Tout ce qui n'est pas listé comme **✅ fourni** est aujourd'hui dessiné à la
main dans `outils/dessine_decor.py` (des placeholders qui marchent, mais laids).
Chaque ligne dit quoi remplacer et par quel type d'asset.

**Format idéal partout** : pixel art, **vue de profil** (side-view), spritesheet
à grille régulière (cases de taille fixe, comme la planche du chat). On sait les
découper automatiquement. Déposer les fichiers dans `~/Downloads/` et donner le
chemin — comme pour le chat, les chats ennemis et le médecin.

---

## ✅ Déjà fournis (ne rien chercher)

| Asset | Fichier | Usage |
|---|---|---|
| Chat joueur | `assets/images/chat.png` (bowpixel) | le héros, animé |
| Chats ennemis | `assets/images/chats/` (Cat Sprite Sheet) | pousseurs + horde |
| Médecin | `assets/images/medecin/` (lablady) | niveau 6, animé |
| Décors des 7 niveaux | `assets/images/fonds/` | les fonds |

---

## 1. Les personnages (antagonistes) — PRIORITÉ HAUTE

Un maître par niveau. Seul le médecin a un vrai sprite. Idéalement une
spritesheet par personnage : **idle + une action** (comme lablady).

| Niveau | Personnage | État | Recherche itch.io |
|---|---|---|---|
| 1 | Le daron (devant sa télé) | à trouver | `side view character sprite`, `man sitting sprite` |
| 2 | La vieille (charentaises) | dessin main | `old woman pixel sprite` |
| 3 | L'enfant à couettes | dessin main | `little girl pixel sprite` |
| 4 | L'influenceur | à trouver | `gamer character sprite`, `youtuber pixel` |
| 5 | Le chef cuisinier | dessin main | `chef pixel sprite`, `cook character` |
| 6 | Le vétérinaire | ✅ (lablady) | — |
| 7 | La famille (couple) | à trouver | `couple pixel sprite`, `happy family sprite` |

## 2. Les objets à pousser — un par niveau

Petits objets qu'on pousse dans le piège. Une image suffit (pas d'animation),
sauf mention.

| Niveau | Objet | État |
|---|---|---|
| 1 | Sac de croquettes | dessin main |
| 2 | Cloche du dîner | dessin main |
| 3 | Canard / jouet de bain | dessin main |
| 4 | Ring light | dessin main |
| 5 | Couvercle de marmite | dessin main |
| 6 | Flacon de somnifères | dessin main |

Recherche : `pixel art items pack`, `household objects pixel`, `food pixel icons`.

## 3. Les pièges mortels (le vrai danger de chaque niveau)

Ceux-ci gagneraient une **animation** (eau qui ondule, flammes, étincelles).

| Niveau | Piège | État | Idéal |
|---|---|---|---|
| 1 | Gamelle de croquettes | dessin main | image |
| 2 | Horde de cent chats | ✅ (planche chat) | — |
| 3 | Aquarium | dessin main | **animé** (eau) |
| 4 | Câble électrique | dessin main | **animé** (étincelles) |
| 5 | Marmite d'eau bouillante | dessin main | **animé** (vapeur, bulles) |
| 7 | Bassin / guirlande | dessin main | **animé** (eau, étincelles) |

Recherche : `animated fire pixel`, `water tile animated`, `electric spark sprite`.

## 4. Les faux pièges (les dangers qui ratent) — beaucoup

Tous dessinés main. De simples icônes suffisent, mais un petit pack les
uniformiserait. Regroupés par thème :

- **Électrique** : prise, câble, multiprise, défibrillateur
- **Cuisine / feu** : four, réchaud, bougie, couteau, gaz
- **Salle de bain / eau** : aquarium, verre cassé
- **Médical** : scalpel, seringue, médicaments, poison, patient
- **Enfant** : maquillage, lit à baldaquin, fil dentaire, poupée
- **Divers** : fenêtre ouverte, cordelette, papillon, pelote de laine, griffures

Recherche : `pixel art props pack`, `trap items pixel`, `medical items pixel`,
`kitchen items pixel`, `toys pixel pack`.

## 5. Le son — PRIORITÉ HAUTE, effort minimal

Le code les joue déjà (`game/audio.py`). Déposer dans `assets/sons/` :

| Fichier | Quand |
|---|---|
| `saut.wav` | le chat saute |
| `atterrissage.wav` | il retombe |
| `mort.wav` | vie grillée (pop / poof) |
| `piege.wav` | faux piège (boing) |
| `reincarnation.wav` | le chat-ange s'envole (sparkle) |
| `win.wav` | fin du jeu |
| `ambiance.wav` | musique de fond en boucle |

**Sources gratuites (CC0)** : [Kenney.nl/audio](https://kenney.nl/assets?q=audio)
(packs SFX cartoon parfaits), [freesound.org](https://freesound.org),
[pixabay.com/sound-effects](https://pixabay.com/sound-effects).

---

## Où chercher, en général

- **itch.io** : le mieux pour le pixel art — chercher `pixel art`, `side view`,
  `sprite sheet`, `top down` (à éviter, on est de profil).
- **opengameart.org**, **kenney.nl** : packs libres (CC0), pas de souci de licence.
- **Toujours** : vue de profil, grille régulière. Éviter l'isométrique et le
  top-down (comme le pack Cat Room, inutilisable ici).

Une fois un asset trouvé, il suffit de le déposer et de me donner le chemin :
je m'occupe du découpage et de l'intégration.

# 🐈 Chat Va Mal

> *Il en a marre de tout. Le problème, c'est que le monde ne veut pas le laisser tranquille.*

Jeu de plateforme / puzzle narratif en 2D, développé en Python.

---

## 🎮 Concept

Le joueur incarne un chat blasé de sa vie et de ses maîtres, qui tente à chaque niveau de mettre un terme à ses péripéties une bonne fois pour toutes pour espérer trouver une meilleure famille. Sauf qu'à chaque tentative, un concours de circonstances absurde et un environnement complètement à côté de la plaque l'en empêchent. Plus il essaie, plus la situation dérape en running gag comique.

**Règle du jeu :** ici, on ne contrôle jamais vraiment la fin qu'on croit voir venir.

### Genre & références
Plateforme / puzzle narratif en 2D, à la croisée de :
- **Getting Over It** — la frustration assumée comme moteur de jeu
- **Happy Tree Friends** / **Wile E. Coyote** — l'humour visuel, le comique de répétition et le décalage entre l'intention du personnage et le résultat

### Le hook
Le twist central : le joueur passe le jeu à essayer d'accomplir ce qu'un jeu vidéo classique cherche justement à éviter. L'inversion complète de l'objectif habituel (« survivre à tout prix » devient « essayer d'échouer ») crée une frustration comique volontaire et un humour noir assumé, mais jamais graphique — tout reste cartoon, absurde et inoffensif à l'écran.

---

## 🕹️ Gameplay core

- Chaque niveau propose un décor fermé avec plusieurs **« occasions »** clairement identifiables par le joueur comme des pièges mortels classiques (chute, eau, feu, écrasement...).
- Le joueur guide le chat vers ces occasions, pensant l'aider à en finir — mais chaque tentative déclenche un **mini-événement scripté** qui annule le danger au dernier moment, souvent de façon ridicule (faux piège / gag).
- Un niveau se termine quand le **« vrai » piège** du niveau se déclenche enfin, faisant perdre une vie sur les **7 disponibles**.
- Ton humoristique, cartoon, jamais réaliste : chutes, écrasements et catastrophes sont stylisés et sans conséquence visuelle choquante.

---

## 📦 Structure du contenu

| # | Décor |
|---|-------|
| 1 | Salon familial |
| 2 | Vieille demeure aux 100 chats |
| 3 | Chambre d'enfant riche |
| 4 | Appart d'influenceur |
| 5 | Cuisine de restaurant |
| 6 | Centre médical |
| 7 | Jardin familial |

Chaque niveau alterne plusieurs faux pièges (gags, fausses alertes) avant un piège final qui fait avancer l'histoire. Sessions courtes par niveau, jeu pensé pour être rejoué et partagé pour ses gags (clips, memes).

---

## 🎨 Direction artistique

- Humour noir cartoon, jamais réaliste ni graphique
- Palette de couleurs vives
- Animations exagérées
- Bruitages comiques accentuant le décalage entre le drame annoncé et la chute absurde

---

## 🎯 Public visé

Joueurs amateurs d'humour noir et de jeux à la difficulté frustrante volontaire (fans de *Getting Over It*, *I Am Bread*), plutôt un public ado / jeune adulte. Format navigateur ou PC, pensé pour être facilement partageable.

---

## 🛠️ Stack technique

Ce projet a été développé en **Python** avec **[Arcade](https://api.arcade.academy/en/latest/)** pour le rendu 2D et la boucle de jeu.

### Prérequis
- Python 3.10+
- pip
- conda

### Installation

```bash
git clone https://github.com/clemence-carcanade/Game_Jam_ESIEE.git
cd Game_Jam_ESIEE
conda create -n <nom_que_vous_souhaitez>
conda activate <nom_que_vous_souhaitez>
pip install -r requirements.txt
```

### Lancer le jeu

```bash
python main.py
```

---

## 📁 Structure du projet (proposition)

Il faudra faire évoluer cette partie au fur et à mesure de l'avancement du code

```
Game_Jam_ESIEE/
├── main.py                 # Point d'entrée
├── requirements.txt
└── README.md
```
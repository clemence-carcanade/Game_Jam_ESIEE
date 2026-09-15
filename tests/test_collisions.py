"""Tests du moteur de collisions, sans ouvrir de fenêtre visible.

    python tests/test_collisions.py

À relancer après TOUTE modification de game/collisions.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import arcade

from game import constantes as C
from game import niveau as module_niveau
from game.chat import Chat
from game.collisions import MoteurCollisions

fenetre = arcade.Window(400, 300, "tests", visible=False)
reussis = echoues = 0


def verifier(libelle, condition, detail=""):
    global reussis, echoues
    if condition:
        reussis += 1
        print(f"  OK   {libelle} {detail}")
    else:
        echoues += 1
        print(f"  RATE {libelle} {detail}")


def carre(x, y, largeur=64, hauteur=64):
    texture = arcade.Texture.create_empty(f"_t{largeur}x{hauteur}", (largeur, hauteur))
    return arcade.Sprite(texture, center_x=x, center_y=y)


def decor(chat_x=100, chat_y=300):
    """Un sol plat, un chat, et des listes vides à remplir selon le test."""
    murs = arcade.SpriteList(use_spatial_hash=True)
    plateformes = arcade.SpriteList(use_spatial_hash=True)
    mortels = arcade.SpriteList(use_spatial_hash=True)
    poussables = arcade.SpriteList()
    zones = arcade.SpriteList()
    for colonne in range(12):
        murs.append(carre(colonne * 64 + 32, 32))
    chat = Chat(chat_x, chat_y)
    moteur = MoteurCollisions(
        chat, murs=murs, plateformes=plateformes, mortels=mortels,
        poussables=poussables, zones=zones,
    )
    return chat, moteur, murs, plateformes, mortels, poussables, zones


def jouer(chat, moteur, images, descendre=False):
    """Fait tourner la boucle de jeu et s'arrête dès que le chat meurt.

    Important : la mort et l'esquive sont signalées sur l'image où elles se
    produisent, pas sur les suivantes. Le vrai jeu réagit immédiatement
    (``griller_une_vie``), donc les tests font pareil.
    """
    contacts = None
    esquive_vue = False
    for _ in range(images):
        chat.calculer_deplacement(1 / 60, moteur.est_au_sol())
        contacts = moteur.mettre_a_jour(descendre=descendre)
        esquive_vue = esquive_vue or contacts.esquive
        if not contacts.vivant:
            break
    contacts.esquive = esquive_vue
    return contacts


print("\n1. Le chat tombe et se pose sur le sol")
chat, moteur, *_ = decor(chat_y=300)
contacts = jouer(chat, moteur, 90)
verifier("posé sur le sol", abs(chat.bottom - 64) < 1, f"bas={chat.bottom}")
verifier("au sol signalé", contacts.au_sol)
verifier("chute non mortelle (moins de 4 tuiles)", contacts.vivant, f"mort={contacts.mort!r}")

print("\n2. Un mur arrête le déplacement horizontal")
chat, moteur, murs, *_ = decor(100, 96)
murs.append(carre(300, 96))
chat.veut_droite = True
jouer(chat, moteur, 120)
verifier("bloqué par le mur", abs(chat.right - 268) < 2, f"droite={chat.right}")

print("\n3. Plateforme traversable : on atterrit dessus par le haut")
chat, moteur, murs, plateformes, *_ = decor(100, 400)
plateformes.append(carre(100, 200, 64, 16))
jouer(chat, moteur, 120)
verifier("posé sur la plateforme", abs(chat.bottom - 208) < 2, f"bas={chat.bottom}")

print("\n4. Plateforme traversable : on la traverse par le bas en sautant")
chat, moteur, murs, plateformes, *_ = decor(100, 96)
plateformes.append(carre(100, 200, 64, 16))
jouer(chat, moteur, 5)
chat.demander_saut()
passe_au_dessus = False
for _ in range(80):
    chat.calculer_deplacement(1 / 60, moteur.est_au_sol())
    moteur.mettre_a_jour()
    if chat.bottom > 208:
        passe_au_dessus = True
verifier("traversée par le bas", passe_au_dessus)
verifier("puis retombé dessus", abs(chat.bottom - 208) < 2, f"bas={chat.bottom}")

print("\n5. Touche bas : on redescend au travers de la plateforme")
chat, moteur, murs, plateformes, *_ = decor(100, 400)
plateformes.append(carre(100, 200, 64, 16))
jouer(chat, moteur, 90)
pose_avant = abs(chat.bottom - 208) < 2
chat.veut_descendre = True
jouer(chat, moteur, 60, descendre=True)
verifier("posé avant", pose_avant)
verifier("retombé au sol après", abs(chat.bottom - 64) < 1, f"bas={chat.bottom}")

print("\n6. Élément mortel : le chat grille une vie")
chat, moteur, murs, plateformes, mortels, *_ = decor(100, 200)
chat.reflexe_moustaches = False
pic = carre(100, 80, 64, 32)
pic.cause_de_mort = "les pointes"
mortels.append(pic)
contacts = jouer(chat, moteur, 120)
verifier("mort signalée", not contacts.vivant and contacts.mort == "les pointes", f"-> {contacts.mort!r}")

print("\n7. Réflexe des moustaches : le chat esquive au lieu de mourir")
chat, moteur, murs, plateformes, mortels, *_ = decor(100, 96)
chat.reflexe_moustaches = True
pic = carre(300, 96, 64, 32)
pic.cause_de_mort = "les pointes"
mortels.append(pic)
chat.veut_droite = True
contacts = jouer(chat, moteur, 120)
verifier("esquive au lieu de mourir", contacts.vivant, f"mort={contacts.mort!r}")
verifier("esquive signalée", contacts.esquive)

print("\n8. Réflexe des pattes : encaisse 4 tuiles, pas 7")
chat, moteur, *_ = decor(100, 4 * 64 + 96)
chat.reflexe_pattes = True
contacts = jouer(chat, moteur, 200)
verifier("survit à 4 tuiles avec le réflexe", contacts.vivant, f"mort={contacts.mort!r}")

chat, moteur, *_ = decor(100, 7 * 64 + 96)
chat.reflexe_pattes = True
contacts = jouer(chat, moteur, 200)
verifier("meurt à 7 tuiles malgré le réflexe", contacts.mort == "la chute", f"-> {contacts.mort!r}")

chat, moteur, *_ = decor(100, 4 * 64 + 96)
chat.reflexe_pattes = False
contacts = jouer(chat, moteur, 200)
verifier("meurt à 4 tuiles sans le réflexe", contacts.mort == "la chute", f"-> {contacts.mort!r}")

print("\n9. Un pouf amortit la chute")
chat, moteur, murs, plateformes, mortels, poussables, zones = decor(100, 7 * 64 + 96)
chat.reflexe_pattes = False
pouf = carre(100, 96, 56, 56)
pouf.amortit = True
poussables.append(pouf)
contacts = jouer(chat, moteur, 200)
verifier("survit en tombant sur le pouf", contacts.vivant, f"mort={contacts.mort!r}")

print("\n10. On pousse un pouf, et il ne traverse pas les murs")
chat, moteur, murs, plateformes, mortels, poussables, zones = decor(100, 96)
pouf = carre(200, 96, 56, 56)
pouf.amortit = True
poussables.append(pouf)
depart = pouf.center_x
chat.veut_droite = True
jouer(chat, moteur, 120)
verifier("le pouf a été poussé", pouf.center_x > depart + 100, f"x={round(pouf.center_x)}")
verifier("le pouf reste au sol", abs(pouf.bottom - 64) < 2, f"bas={pouf.bottom}")

chat, moteur, murs, plateformes, mortels, poussables, zones = decor(100, 96)
murs.append(carre(400, 96))
pouf = carre(300, 96, 56, 56)
poussables.append(pouf)
chat.veut_droite = True
jouer(chat, moteur, 150)
verifier("le pouf est bloqué par le mur", pouf.right <= 372, f"droite={pouf.right}")

print("\n11. Réflexe d'agrippement : impossible de tomber en marchant")
chat, moteur, murs, *_ = decor(100, 96)
chat.reflexe_agrippe = True
chat.veut_droite = True
jouer(chat, moteur, 200)
verifier("reste sur le rebord", chat.center_y > 64, f"y={round(chat.center_y)}")

chat, moteur, murs, *_ = decor(100, 96)
chat.reflexe_agrippe = False
chat.veut_droite = True
contacts = jouer(chat, moteur, 200)
verifier("tombe sans le réflexe", chat.center_y < 64, f"y={round(chat.center_y)}")

print("\n12. Zone (bouton) détectée sans bloquer le passage")
chat, moteur, murs, plateformes, mortels, poussables, zones = decor(100, 96)
zones.append(carre(300, 72, 64, 16))
chat.veut_droite = True
touche = False
for _ in range(120):
    chat.calculer_deplacement(1 / 60, moteur.est_au_sol())
    if moteur.mettre_a_jour().zones:
        touche = True
verifier("bouton détecté", touche)
verifier("le chat n'a pas été bloqué", chat.center_x > 320, f"x={round(chat.center_x)}")

print("\n13. Le niveau 1 se charge et le chat tient sur sa plateforme")
niveau = module_niveau.charger(1)
chat = Chat(*niveau.depart_chat)
moteur = MoteurCollisions(
    chat, murs=niveau.murs, plateformes=niveau.plateformes,
    mortels=niveau.mortels, poussables=niveau.poussables, zones=niveau.zones,
)
contacts = jouer(chat, moteur, 60)
verifier("chat posé sur la plateforme de départ", contacts.au_sol, f"y={round(chat.center_y)}")
verifier("il ne meurt pas tout seul", contacts.vivant, f"mort={contacts.mort!r}")

print(f"\n{reussis} tests réussis, {echoues} échec(s)")
fenetre.close()
raise SystemExit(1 if echoues else 0)

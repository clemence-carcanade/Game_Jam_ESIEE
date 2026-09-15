"""Genere les sept niveaux de Sept Vies.

    python outils/genere_niveaux.py

Chaque niveau a sa propre geometrie : le chemin qui monte n'est jamais le meme,
et le piege n'est pas au meme endroit. Le script **verifie** ce qu'il produit :

* chaque meuble forme un rectangle plein (sinon il est dessine plusieurs fois) ;
* chaque saut du parcours est faisable (2 cases de haut, 3 de large au plus) ;
* la colonne ou tombe l'objet est degagee jusqu'au sol, et le piege est dessous.

Si une de ces regles casse, le script le dit et n'ecrit rien.
"""

import json
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent.parent / "niveaux"
L, H = 20, 9                      # 20 cases sur 9 rangees, 64 px la case
SOL = H - 1

SAUT_MAX_HAUT = 2                 # rangees franchissables d'un saut
SAUT_MAX_LARGE = 3                # cases franchissables d'un saut


def dessus(rangee):
    """Altitude du dessus d'une plateforme, en rangees au-dessus du sol."""
    return SOL - rangee


# --- les sept foyers --------------------------------------------------------
# marches : du bas vers le haut, (rangee, colonne debut, colonne fin)
# meubles : (caractere, rangee debut, rangee fin, colonne debut, colonne fin)
NIVEAUX = [
    dict(
        n=1, titre="Salon, 20h : encore les memes croquettes", maitre="le daron",
        aide="Le sac de croquettes est en haut de l etagere. Fais-le tomber dans la gamelle.",
        piege="Le sac se renverse dans la gamelle. Les croquettes du fond, celles qui sentent.",
        mort="Etouffe avec les croquettes. Une vie de moins, une maison de plus.",
        marches=[(6, 5, 6), (5, 1, 3), (4, 4, 6), (2, 6, 8)],
        meubles=[("3", 5, 7, 1, 3), ("2", 6, 7, 5, 6), ("4", 5, 7, 12, 14),
                 ("5", 6, 7, 15, 17), ("p", 4, 7, 10, 11), ("w", 1, 2, 13, 15),
                 ("f", 4, 6, 18, 18)],
        objet=7, pousse="d", piege_colonne=9, depart=8,
        deco=[(7, "8", 4), (7, "6", 7), (2, "9", 2), (3, "c", 3), (3, "c", 4)],
    ),
    dict(
        n=2, titre="La vieille demeure : cent chats, une gamelle", maitre="la vieille",
        aide="L arbre a chat est tout en haut, a droite. Fais-le basculer et place-toi dessous.",
        piege="L arbre a chat penche. Cent chats regardent ailleurs.",
        mort="Ecrase sous l arbre a chat. Personne n a rien vu.",
        marches=[(6, 15, 17), (4, 12, 14), (2, 9, 11)],
        meubles=[("4", 6, 7, 15, 17), ("3", 5, 7, 1, 3), ("2", 6, 7, 5, 6),
                 ("=", 4, 4, 12, 14), ("=", 2, 2, 9, 11), ("p", 4, 7, 17, 18)],
        objet=10, pousse="g", piege_colonne=8, depart=4,
        deco=[(7, "8", 8), (7, "6", 13), (2, "9", 2), (3, "c", 5), (3, "c", 6)],
    ),
    dict(
        n=3, titre="La chambre de l enfant riche", maitre="l enfant",
        aide="Le jouet de bain est en haut de la bibliotheque. Fais-le tomber dans l aquarium.",
        piege="L aquarium deborde. L eau est froide.",
        mort="Noye dans l aquarium. Elle croira a un jeu.",
        marches=[(6, 2, 4), (4, 2, 4), (2, 2, 4)],
        meubles=[("=", 6, 6, 2, 4), ("=", 4, 4, 2, 4), ("=", 2, 2, 2, 4),
                 ("3", 5, 7, 8, 10), ("4", 5, 7, 13, 15), ("5", 6, 7, 16, 17),
                 ("w", 1, 2, 13, 15)],
        objet=3, pousse="d", piege_colonne=5, depart=7,
        deco=[(7, "8", 12), (7, "6", 18), (2, "9", 7), (3, "c", 9), (3, "c", 10)],
    ),
    dict(
        n=4, titre="L appart de l influenceur", maitre="l influenceur",
        aide="La ring light est en equilibre la-haut. Son cable traine juste en dessous.",
        piege="Le cable est denude. Il grezille.",
        mort="Electrocute en direct. Trois cent mille vues.",
        marches=[(6, 8, 10), (4, 5, 7), (2, 8, 10)],
        meubles=[("=", 6, 6, 8, 10), ("=", 4, 4, 5, 7), ("=", 2, 2, 8, 10),
                 ("3", 5, 7, 1, 3), ("4", 5, 7, 14, 16), ("5", 6, 7, 17, 18)],
        objet=9, pousse="d", piege_colonne=11, depart=6,
        deco=[(7, "8", 5), (7, "6", 13), (2, "9", 2), (3, "c", 4), (3, "c", 5)],
    ),
    dict(
        n=5, titre="La cuisine du restaurant, en plein rush", maitre="le chef",
        aide="La marmite bout sans surveillance. Monte jusqu a l etagere et fais tomber le couvercle.",
        piege="La marmite deborde. Personne ne regarde.",
        mort="Tombe dans l eau bouillante. Le service continue.",
        marches=[(6, 3, 5), (4, 7, 9), (2, 11, 13)],
        meubles=[("=", 6, 6, 3, 5), ("=", 4, 4, 7, 9), ("=", 2, 2, 11, 13),
                 ("4", 5, 7, 16, 18), ("2", 6, 7, 1, 2)],
        objet=12, pousse="d", piege_colonne=14, depart=6,
        deco=[(7, "8", 11), (7, "6", 9), (2, "9", 17), (3, "c", 2), (3, "c", 3)],
    ),
    dict(
        n=6, titre="Le cabinet medical", maitre="le docteur",
        aide="Le flacon d anesthesiant est en haut. Endors le medecin d abord, sinon il te soignera.",
        piege="Le medecin s est endormi sur son bureau.",
        mort="Cette fois, personne n est venu recoudre.",
        marches=[(6, 15, 17), (4, 12, 14), (2, 9, 11)],
        meubles=[("=", 6, 6, 15, 17), ("=", 4, 4, 12, 14), ("=", 2, 2, 9, 11),
                 ("4", 5, 7, 2, 4), ("5", 6, 7, 5, 6), ("p", 4, 7, 17, 18),
                 ("w", 1, 2, 1, 3)],
        objet=10, pousse="g", piege_colonne=8, depart=13,
        deco=[(7, "8", 7), (7, "6", 12), (2, "9", 6), (3, "c", 5), (3, "c", 6)],
    ),
]

DERNIER = dict(
    n=7, titre="Le jardin : il ne veut plus mourir", maitre="la famille",
    aide="Cette fois il faut rentrer vivant. Ils t attendent en haut, a droite.",
    mort="Pas comme ca. Pas maintenant. On recommence.",
    marches=[(6, 5, 7), (4, 9, 11), (2, 13, 15)],
    meubles=[("=", 6, 6, 5, 7), ("=", 4, 4, 9, 11), ("=", 2, 2, 13, 15),
             ("3", 5, 7, 1, 3), ("4", 6, 7, 16, 18), ("w", 1, 2, 1, 3)],
    sortie=14, depart=8,
    deco=[(7, "8", 4), (7, "6", 12), (2, "9", 17), (3, "c", 9), (3, "c", 10)],
)


def salle():
    carte = [["." for _ in range(L)] for _ in range(H)]
    for ligne in range(H):
        carte[ligne][0] = carte[ligne][L - 1] = "#"
    for colonne in range(L):
        carte[0][colonne] = carte[SOL][colonne] = "#"
    return carte


def construire(spec, dernier=False):
    carte = salle()
    for caractere, r0, r1, c0, c1 in spec["meubles"]:
        for ligne in range(r0, r1 + 1):
            for colonne in range(c0, c1 + 1):
                carte[ligne][colonne] = caractere
    for ligne, caractere, colonne in spec["deco"]:
        if carte[ligne][colonne] == ".":
            carte[ligne][colonne] = caractere

    haute = spec["marches"][-1]
    if dernier:
        carte[haute[0] - 1][spec["sortie"]] = "G"
    else:
        carte[haute[0] - 1][spec["objet"]] = "O"
        carte[SOL - 1][spec["piege_colonne"]] = "1"
    carte[SOL - 1][spec["depart"]] = "C"
    return carte


def verifier(spec, carte, dernier=False):
    """Retourne la liste des problemes trouves. Vide = le niveau tient debout."""
    soucis = []

    # 1. chaque meuble est un rectangle plein (les etageres '=' sont a part :
    #    il y en a plusieurs, separees, dans le meme niveau)
    cases = {}
    for ligne, contenu in enumerate(carte):
        for colonne, caractere in enumerate(contenu):
            if caractere in "#.=COG1":
                continue
            cases.setdefault(caractere, []).append((ligne, colonne))
    for caractere, points in cases.items():
        lignes = [l for l, _ in points]
        colonnes = [c for _, c in points]
        attendu = (max(lignes) - min(lignes) + 1) * (max(colonnes) - min(colonnes) + 1)
        if attendu != len(points):
            soucis.append(f"le meuble '{caractere}' n'est pas un rectangle plein")

    # 2. chaque marche est atteignable depuis la precedente
    precedente = (SOL, 0, L - 1)                    # le sol
    for rangee, c0, c1 in spec["marches"]:
        monte = dessus(rangee) - dessus(precedente[0])
        if monte > SAUT_MAX_HAUT:
            soucis.append(f"la marche rangee {rangee} est {monte} cases trop haut")
        ecart = max(c0 - precedente[2], precedente[1] - c1, 0)
        if ecart > SAUT_MAX_LARGE:
            soucis.append(f"la marche rangee {rangee} est {ecart} cases trop loin")
        precedente = (rangee, c0, c1)

    # 3. l'objet tombe-t-il jusqu'au piege ?
    if not dernier:
        rangee, c0, c1 = spec["marches"][-1]
        chute = c1 + 1 if spec["pousse"] == "d" else c0 - 1
        if chute != spec["piege_colonne"]:
            soucis.append(f"l objet tombe colonne {chute}, le piege est colonne {spec['piege_colonne']}")
        for ligne in range(rangee, SOL):
            if carte[ligne][chute] not in ".1COG":
                soucis.append(f"la colonne de chute {chute} est bouchee rangee {ligne}")
                break
    return soucis


def ecrire():
    DOSSIER.mkdir(exist_ok=True)
    tout_va_bien = True

    for spec in NIVEAUX + [DERNIER]:
        dernier = spec is DERNIER
        carte = construire(spec, dernier)
        soucis = verifier(spec, carte, dernier)
        etat = "ok" if not soucis else "PROBLEME"
        print(f"niveau {spec['n']} : {spec['titre'][:42]:44s} {etat}")
        for souci in soucis:
            print(f"    - {souci}")
            tout_va_bien = False
        if soucis:
            continue

        entete = {"titre": spec["titre"], "maitre": spec["maitre"], "aide": spec["aide"],
                  "message_mort": spec["mort"]}
        if dernier:
            entete["survivre"] = True
        else:
            entete["message_piege"] = spec["piege"]

        lignes = ["".join(ligne) for ligne in carte]
        (DOSSIER / f"niveau_{spec['n']}.txt").write_text(
            json.dumps(entete, ensure_ascii=True) + "\n" + "\n".join(lignes) + "\n",
            encoding="utf-8",
        )

    return tout_va_bien


if __name__ == "__main__":
    raise SystemExit(0 if ecrire() else 1)

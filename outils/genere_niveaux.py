"""Genere game/les_niveaux.py : les sept niveaux, verifies avant ecriture.

    python outils/genere_niveaux.py

Plus de fichiers .txt : un niveau en Python porte sa carte, ses textes ET ses
faux pieges scriptes. Le script verifie chaque niveau et refuse d'ecrire s'il
est casse (meuble troue, saut infaisable, colonne de chute bouchee).

Les faux pieges sont des lettres minuscules posees sur la carte ; leur effet
est decrit a cote. Regle n.1 du jeu : tout ce qui a l'air mortel doit rater.

    effet "message"      il ne se passe rien de grave, et on le dit
    effet "projection"   le chat est lance/pousse (il retombe sur ses pattes)
    effet "soin"         quelqu'un le sauve : retour au point de depart
    effet "deguisement"  humilie, colore, vivant
    effet "sac"          la tete coincee dedans, il fonce dans le decor
    declenchement        "action" = touche E, "contact" = toucher la zone
"""

from pathlib import Path

SORTIE_PY = Path(__file__).resolve().parent.parent / "game" / "les_niveaux.py"
L, H = 22, 11
SOL = H - 1
SAUT_MAX_HAUT = 2
SAUT_MAX_LARGE = 3

# lettres deja prises par le mobilier de game/niveau.py
LETTRES_MOBILIER = set("bcfpw")


def dessus(rangee):
    return SOL - rangee


NIVEAUX = [
    dict(
        n=1, titre="Salon, 20h : encore les memes croquettes", maitre="le daron",
        aide="Le sac de croquettes est tout en haut. Fais-le tomber dans la gamelle.",
        piege="Le sac se renverse dans la gamelle. Les croquettes du fond, celles qui sentent.",
        mort="Etouffe avec les croquettes. Une vie de moins, une maison de plus.",
        marches=[(8, 5, 6), (7, 1, 3), (6, 4, 6), (4, 7, 9), (2, 9, 11)],
        meubles=[("3", 7, 9, 1, 3), ("2", 8, 9, 5, 6), ("=", 6, 6, 4, 6),
                 ("=", 4, 4, 7, 9), ("=", 2, 2, 9, 11), ("p", 6, 9, 13, 14),
                 ("4", 7, 9, 16, 18), ("5", 8, 9, 19, 20), ("w", 1, 2, 16, 18),
                 ("f", 4, 6, 20, 20)],
        objet=10, pousse="d", piege_colonne=12, depart=8,
        deco=[(9, "8", 7), (9, "6", 11), (2, "9", 2), (3, "c", 4), (3, "c", 5)],
        lettres={
            "j": dict(pos=[(9, 4)], declenchement="contact", recharge=6.0,
                      texte="Saute d aussi haut que tu veux : il retombe sur ses pattes."),
        },
    ),
    dict(
        n=2, titre="La vieille demeure : cent chats, une gamelle", maitre="la vieille",
        aide="Fais basculer l arbre a chat du haut du vaisselier, et place-toi dessous.",
        piege="L arbre a chat penche. Cent chats regardent ailleurs.",
        mort="Ecrase sous l arbre a chat. Personne n a rien vu.",
        piege_image="coussin",
        message_attente="L arbre a chat est encore debout. Fais-le basculer d abord.",
        marches=[(8, 16, 17), (7, 19, 20), (6, 14, 16), (4, 11, 13), (2, 8, 10)],
        meubles=[("2", 8, 9, 16, 17), ("3", 7, 9, 18, 20), ("=", 6, 6, 14, 16),
                 ("=", 4, 4, 11, 13), ("=", 2, 2, 8, 10), ("4", 7, 9, 1, 3),
                 ("p", 6, 9, 5, 6), ("f", 4, 6, 1, 1)],
        objet=9, pousse="g", piege_colonne=7, depart=12,
        deco=[(9, "8", 8), (9, "6", 13), (2, "9", 19), (3, "c", 17), (3, "c", 18)],
        lettres={
            "k": dict(pos=[(6, 20)], declenchement="contact", recharge=8.0, image="chat_gris",
                      effet="projection", vitesse=(-9, 14),
                      texte="Un autre chat le pousse dans le vide. Les coussins l attendaient."),
            "v": dict(pos=[(9, 10)], declenchement="action", image="vieille",
                      texte="La charentaise s abat sur lui. Epaisse comme un matelas. Rien."),
            "l": dict(pos=[(9, 4)], declenchement="action", effet="soin", image="panier_linge",
                      texte="Range dans le buffet avec le linge. Il ressort par en bas, plie, vivant."),
        },
    ),
    dict(
        n=3, titre="La chambre de l enfant riche", maitre="l enfant",
        aide="Le jouet de bain est au sommet du baldaquin. Fais-le tomber dans l aquarium.",
        piege="L aquarium deborde. L eau est froide.",
        mort="Noye dans l aquarium. Elle croira a un jeu.",
        piege_image="aquarium",
        message_attente="L aquarium est paisible. Le jouet de bain d abord, tout en haut.",
        marches=[(8, 2, 3), (6, 2, 4), (4, 2, 4), (2, 2, 4)],
        meubles=[("2", 8, 9, 2, 3), ("=", 6, 6, 2, 4), ("=", 4, 4, 2, 4),
                 ("=", 2, 2, 2, 4), ("3", 7, 9, 9, 11), ("4", 7, 9, 14, 16),
                 ("5", 8, 9, 18, 19), ("w", 1, 2, 14, 16), ("p", 6, 9, 12, 13)],
        objet=3, pousse="d", piege_colonne=5, depart=7,
        deco=[(9, "8", 13), (9, "6", 20), (2, "9", 7), (3, "c", 9), (3, "c", 10)],
        lettres={
            "e": dict(pos=[(9, 8)], declenchement="contact", recharge=9.0, image="enfant",
                      effet="projection", vitesse=(4, 19),
                      texte="Attrape et lance en l air facon poupee. Il retombe sur ses pattes. Elle applaudit."),
            "m": dict(pos=[(9, 17)], declenchement="action", effet="deguisement", image="maquillage",
                      teinte=(255, 150, 200), duree=5.0,
                      texte="Maquille, coiffe, deguise. Humiliant. Mais vivant."),
        },
    ),
    dict(
        n=4, titre="L appart de l influenceur", maitre="l influenceur",
        aide="La ring light est perchee la-haut. Son cable traine juste dessous.",
        piege="Le cable est denude. Il gresille.",
        mort="Electrocute en direct. Trois cent mille vues.",
        piege_image="cable",
        message_attente="Le cable est encore bien range. Fais tomber la ring light.",
        marches=[(8, 9, 10), (6, 6, 8), (4, 9, 11), (2, 6, 8)],
        meubles=[("2", 8, 9, 9, 10), ("=", 6, 6, 6, 8), ("=", 4, 4, 9, 11),
                 ("=", 2, 2, 6, 8), ("3", 7, 9, 1, 3), ("4", 7, 9, 15, 17),
                 ("5", 8, 9, 18, 19), ("w", 1, 2, 15, 17)],
        objet=7, pousse="g", piege_colonne=5, depart=12,
        deco=[(9, "8", 6), (9, "6", 14), (2, "9", 2), (3, "c", 3), (3, "c", 4)],
        lettres={
            "g": dict(pos=[(9, 20)], declenchement="action", effet="projection", image="griffures",
                      vitesse=(-3, 15),
                      texte="Il grimpe au mur pour s echapper. Glisse. Retombe. Story instantanee."),
            "n": dict(pos=[(9, 13)], declenchement="action", image="plante",
                      texte="Il mange la plante pour s empoisonner. La vomit. Vivant, et pas fier."),
        },
    ),
    dict(
        n=5, titre="La cuisine du restaurant, en plein rush", maitre="le chef",
        aide="La marmite bout sans surveillance. Fais tomber le couvercle, et saute.",
        piege="La marmite est ouverte. Personne ne regarde.",
        mort="Tombe dans l eau bouillante. Le service continue.",
        piege_image="marmite",
        message_attente="Le couvercle est encore sur la marmite. Fais-le tomber.",
        marches=[(8, 3, 4), (6, 6, 8), (4, 10, 12), (2, 14, 16)],
        meubles=[("2", 8, 9, 3, 4), ("=", 6, 6, 6, 8), ("=", 4, 4, 10, 12),
                 ("=", 2, 2, 14, 16), ("4", 7, 9, 19, 20), ("5", 8, 9, 12, 13),
                 ("p", 6, 9, 1, 2)],
        objet=15, pousse="d", piege_colonne=17, depart=6,
        deco=[(9, "8", 8), (9, "6", 11), (2, "9", 19), (3, "c", 5), (3, "c", 6)],
        lettres={
            "u": dict(pos=[(9, 14)], declenchement="action", image="couteau",
                      texte="Le couteau bascule du plan de travail... et se plante a cote. Rate."),
            "h": dict(pos=[(9, 10)], declenchement="action", image="chef",
                      texte="Provoque, le chef s ecroule : crise cardiaque. Il n aura pas le temps de le tuer."),
        },
    ),
    dict(
        n=6, titre="Le cabinet medical", maitre="le docteur",
        aide="Le flacon d anesthesiant est en haut. Endors le medecin d abord, sinon il soigne tout.",
        piege="Le medecin s est endormi sur son bureau.",
        mort="Cette fois, personne n est venu recoudre.",
        piege_image="medecin",
        message_attente="Le medecin est reveille. Il te recoudrait. Le flacon d abord.",
        marches=[(8, 17, 18), (6, 14, 16), (4, 11, 13), (2, 8, 10)],
        meubles=[("2", 8, 9, 17, 18), ("=", 6, 6, 14, 16), ("=", 4, 4, 11, 13),
                 ("=", 2, 2, 8, 10), ("4", 7, 9, 2, 4), ("5", 8, 9, 5, 6),
                 ("p", 6, 9, 19, 20), ("w", 1, 2, 2, 4)],
        objet=9, pousse="g", piege_colonne=7, depart=15,
        deco=[(9, "8", 8), (9, "6", 13), (2, "9", 6), (3, "c", 5), (3, "c", 6)],
        lettres={
            "s": dict(pos=[(9, 10)], declenchement="action", effet="soin", image="scalpel",
                      texte="Le scalpel. Precis. Le medecin le recoud en huit minutes, montre en main."),
            "q": dict(pos=[(9, 12)], declenchement="action", effet="soin", image="seringue",
                      texte="La seringue du medecin. Reanime. Et vaccine, en prime."),
            "d": dict(pos=[(9, 16)], declenchement="action", effet="soin", image="patient",
                      texte="Il leche le patient contagieux. Gueri en une nuit. Ce medecin est trop fort."),
        },
    ),
]

DERNIER = dict(
    n=7, titre="Le jardin : il ne veut plus mourir", maitre="la famille",
    aide="Cette fois il faut rentrer vivant. Evite le bassin. Ils t attendent en haut, a droite.",
    mort="Pas comme ca. Pas maintenant. On recommence.",
    survivre=True, reflexes_coupes=["moustaches"],
    cause_mortelle="l eau du bassin",
    marches=[(8, 4, 5), (6, 7, 9), (4, 11, 13), (2, 15, 17)],
    meubles=[("2", 8, 9, 4, 5), ("=", 6, 6, 7, 9), ("=", 4, 4, 11, 13),
             ("=", 2, 2, 15, 17), ("3", 7, 9, 1, 2), ("w", 1, 2, 2, 4)],
    mortels=[(9, 10), (9, 11), (9, 12), (9, 16), (9, 17)],   # le bassin, en deux plans d eau
    sortie=(1, 18), depart=7,
    deco=[(9, "6", 3), (9, "6", 20), (2, "9", 19), (3, "c", 6), (3, "c", 7)],
    lettres={
        "y": dict(pos=[(8, 9)], declenchement="contact", recharge=10.0, image="papillon",
                  texte="Un papillon. Il le suit des yeux. Le bassin est juste la. Pas cette fois."),
        "z": dict(pos=[(9, 14)], declenchement="action", image="pelote",
                  texte="Une balle de laine. Non. Il sait exactement comment ca finit."),
    },
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
    for ligne, caractere, colonne in spec.get("deco", []):
        if carte[ligne][colonne] == ".":
            carte[ligne][colonne] = caractere
    for lettre, effet in spec.get("lettres", {}).items():
        for ligne, colonne in effet["pos"]:
            if carte[ligne][colonne] != ".":
                raise SystemExit(
                    f"niveau {spec['n']} : la lettre '{lettre}' tombe sur "
                    f"'{carte[ligne][colonne]}' en ({ligne},{colonne})")
            carte[ligne][colonne] = lettre
    for ligne, colonne in spec.get("mortels", []):
        carte[ligne][colonne] = "X"

    def poser_unique(ligne, colonne, caractere):
        if carte[ligne][colonne] != ".":
            raise SystemExit(
                f"niveau {spec['n']} : '{caractere}' tombe sur "
                f"'{carte[ligne][colonne]}' en ({ligne},{colonne})")
        carte[ligne][colonne] = caractere

    haute = spec["marches"][-1]
    if dernier:
        poser_unique(*spec["sortie"], "G")
    else:
        poser_unique(haute[0] - 1, spec["objet"], "O")
        poser_unique(SOL - 1, spec["piege_colonne"], "1")
    poser_unique(SOL - 1, spec["depart"], "C")
    return carte


def verifier(spec, carte, dernier=False):
    soucis = []

    for lettre in spec.get("lettres", {}):
        if lettre in LETTRES_MOBILIER:
            soucis.append(f"la lettre '{lettre}' est deja prise par le mobilier")

    cases = {}
    for ligne, contenu in enumerate(carte):
        for colonne, caractere in enumerate(contenu):
            if caractere in "#.=COGX1689" or caractere in spec.get("lettres", {}):
                continue
            cases.setdefault(caractere, []).append((ligne, colonne))
    for caractere, points in cases.items():
        if len(points) == 1:
            continue
        lignes = [l for l, _ in points]
        colonnes = [c for _, c in points]
        attendu = (max(lignes) - min(lignes) + 1) * (max(colonnes) - min(colonnes) + 1)
        if attendu != len(points):
            soucis.append(f"le meuble '{caractere}' n est pas un rectangle plein")

    precedente = (SOL, 0, L - 1)
    for rangee, c0, c1 in spec["marches"]:
        monte = dessus(rangee) - dessus(precedente[0])
        if monte > SAUT_MAX_HAUT:
            soucis.append(f"marche rangee {rangee} : {monte} cases trop haut")
        ecart = max(c0 - precedente[2], precedente[1] - c1, 0)
        if ecart > SAUT_MAX_LARGE:
            soucis.append(f"marche rangee {rangee} : {ecart} cases trop loin")
        precedente = (rangee, c0, c1)

    if not dernier:
        rangee, c0, c1 = spec["marches"][-1]
        chute = c1 + 1 if spec["pousse"] == "d" else c0 - 1
        if chute != spec["piege_colonne"]:
            soucis.append(f"l objet tombe colonne {chute}, le piege est colonne {spec['piege_colonne']}")
        for ligne in range(rangee, SOL):
            if carte[ligne][chute] not in ".1C":
                soucis.append(f"colonne de chute {chute} bouchee rangee {ligne} ('{carte[ligne][chute]}')")
                break
    return soucis


def ecrire():
    morceaux = []
    tout_va_bien = True

    for spec in NIVEAUX + [DERNIER]:
        dernier = spec is DERNIER
        carte = construire(spec, dernier)
        soucis = verifier(spec, carte, dernier)
        etat = "ok" if not soucis else "PROBLEME"
        print(f"niveau {spec['n']} : {spec['titre'][:44]:46s} {etat}")
        for souci in soucis:
            print(f"    - {souci}")
            tout_va_bien = False
        if soucis:
            continue

        entree = {
            "titre": spec["titre"], "maitre": spec["maitre"], "aide": spec["aide"],
            "message_mort": spec["mort"],
        }
        if dernier:
            entree["survivre"] = True
            entree["reflexes_coupes"] = spec.get("reflexes_coupes", [])
            entree["cause_mortelle"] = spec.get("cause_mortelle", "")
        else:
            entree["message_piege"] = spec["piege"]
            if spec.get("piege_image"):
                entree["piege_image"] = spec["piege_image"]
            if spec.get("message_attente"):
                entree["message_attente"] = spec["message_attente"]
        entree["carte"] = ["".join(ligne) for ligne in carte]
        entree["faux_pieges"] = {
            lettre: {cle: valeur for cle, valeur in effet.items() if cle != "pos"}
            for lettre, effet in spec.get("lettres", {}).items()
        }
        morceaux.append(entree)

    if not tout_va_bien:
        return False

    lignes = ['"""Les sept niveaux de Sept Vies.',
              "",
              "NE PAS EDITER A LA MAIN : ce fichier est produit et verifie par",
              "outils/genere_niveaux.py. C est la-bas qu on modifie un niveau.",
              '"""', "", "NIVEAUX = ["]
    for entree in morceaux:
        lignes.append("    {")
        for cle, valeur in entree.items():
            if cle == "carte":
                lignes.append('        "carte": [')
                for rang in valeur:
                    lignes.append(f'            "{rang}",')
                lignes.append("        ],")
            else:
                lignes.append(f'        "{cle}": {valeur!r},')
        lignes.append("    },")
    lignes.append("]")
    SORTIE_PY.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"\n{len(morceaux)} niveaux ecrits dans {SORTIE_PY.name}")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if ecrire() else 1)

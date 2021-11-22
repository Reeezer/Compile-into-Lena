# Projet Compilateurs

## Introduction

Le but du projet est de générer une image au lieu d'un code assembleur classique.

L'image pourra donc être lancée dans un intérpreteur (comme svm.py vu en cours), afin d'exécuter le code contenu dedans.

Il y a donc 2 codes à faire:
- générer l'image
- interpréter l'image

Admettons un code assembleur avec 30 instructions, l'image aura donc 36 pixels (30 utiles et 6 morts à la fin), afin de former une image carrée.

Les pixels seront lu de gauche à droite, de haut en bas.

## Cross-projet traitement images

L'idée serait ensuite, depuis une image "code", de cacher les informations du code derrière une autre image, et de pouvoir récupérer ensuite l'image "code"

(comme vu en cours avec l'éléphant #petitchien)

## Code couleur

Chaque instruction est représentée avec une couleur différente.

Par exemple :
- if _rouge clair_
- elif _rouge un peumoins clair_
- else _rouge foncé_
- while _bleu_
- bloc condition _gris_
- bloc "mort" (pixels inutiles à la fin) _noir_

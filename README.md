# Projet Compilateurs

## Participants

- [Campana Luca](https://github.com/LuEnCam)
- [Muller Léon](https://github.com/Reeezer)
- [Girardin Jarod](https://github.com/girardinj)

## Introduction

Le but du projet est de générer une image couleur RGB de type png d'après un code, puis d'interpréter le code contenu dans cette image.

Il y a donc 2 codes à faire:
- générer l'image à partir d'un code: transcription
- interpréter le code de l'image: analyse lexical, grammaticale, compilation/interprétation

Les pixels seront lu de gauche à droite et de haut en bas.

L'idée serait ensuite, depuis une image "code", de cacher les informations du code derrière une autre image, et de pouvoir récupérer ensuite l'image "code".

(comme avec l'éléphant #petitchien) --> vu en traitement d'image

## Code couleur

Chaque instruction est représentée avec une couleur différente.

Travailler en HSB pour pouvoir avoir 256 couleurs différentes pour des instructions (ce qui est suffisant), ainsi que des teintes de celles-ci pour les variables par exemple.

Par exemple :
- if _rouge clair_
- elif _rouge un peumoins clair_
- else _rouge foncé_
- while _bleu_
- bloc condition _gris_
- bloc "mort" (pixels inutiles) _noir_

## Améliorations possibles

- Au lieu de lire de haut en bas, ajouter des teintes de gris donnant l'ordre de lecture, afin de pouvoir réorganiser les lignes et de générer une image plus harmonieuse (dessin) (attention aux variables, il faut les utiliser d'une manière différente).
    - Au lieu de changer la teinte de gris d'une ligne entière, modifier que le premier pixel avec un "pixel d'index" => même problème que les variables, il ne peut y avoir que 256 lignes par défaut.
- Au lieu d'avoir des couleurs fixes par instruction, ajouter un dictionnaire de couleurs à la fin et générer le code couleurs dynamiquement.

## Sources
- https://www.sentinelone.com/blog/hiding-code-inside-images-malware-steganography/ 
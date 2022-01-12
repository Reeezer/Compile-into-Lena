# Projet Compilateurs

## Participants

- [Campana Luca](https://github.com/LuEnCam)
- [Muller Léon](https://github.com/Reeezer)
- [Girardin Jarod](https://github.com/girardinj)

## Introduction

Le but du projet est de générer une image couleur RGB de type png à partir d'un code, puis de pouvoir interpréter l'image. 

Le projet sera donc décliné en deux parties:
- une partie de génération de l'image à partir d'un code : **partie de transcription**
- une partie d'interprétation du code de l'image: **analyse lexical, grammaticale, compilation/interprétation**

Chaque instruction sera représentée (convertie) en pixel couleur pour être représentée sur une image.

Les pixels seront lu de gauche à droite et de haut en bas.

L'idée serait ensuite, depuis une image "codée en pixels", de la dissimuler dans une autre image (image "réelle"), et de pouvoir récupérer ensuite l'image "codée".

(comme avec l'exemple vu en cours de traitement d'image où un éléphant était caché dans une image d'un billet américain --> #petitchien)

## Code couleur

Chaque instruction est représentée avec une couleur différente.

Par exemple :
- *if* - *rouge clair*
- *elif* - *rouge un peumoins clair*
- *else* - *rouge foncé*
- *while* - *bleu*
- *bloc condition* - *gris*
- *bloc "mort"* (pixels inutiles) -  *noir*

## Enrichissement des opérations

Le projet exploite le fichier "svm.py" (Simple Virtual Machine (or Stupid Virtual Machine)). Plusieurs instructions sont déjà implémentée en son sein permettant de l'arithmétique de base et autres fonctions basiques ( PUSHC \<val\>,  PUSHV \<id\>, SET \<id\>, PRINT, ADD, SUB, MUL, DIV, USUB, JMP, JIZ, JINZ). Un objectif du projet serait d'enrichir les opérations possibles en pouvant notamment implémenter le modulo (MOD), les if/else (IF/ELIF), les puissances (POW), etc...

## Syntaxe stricte

Le projet permettra de faire une analyse stricte du code à compiler en image. L'idée est de renvoyer des informations claires sur les erreurs rencontrées à l'utilisateur de notre compilateur. Par exemple, les puissances pourront être utilisées avec l'opérateur "^" et non pas avec "\*\*". Ceci devrait retourner une opération invalide.

## Analyse sémantique

Le projet souhaite pouvoir faire un contrôle du typage des variables et de mettre en place la gestion des fonctions. Par types, le must have doit être au minimum les entiers (int) et nombres flottants (float). L'idée serait d'avoir aussi des chaînes de caractères (string).

Faire un arbre ou un tableau des symboles. Voir si des variables 

## Améliorations possibles

- Au lieu de lire de haut en bas, ajouter des teintes de gris donnant l'ordre de lecture, afin de pouvoir réorganiser les lignes et de générer une image plus harmonieuse (dessin) (attention aux variables, il faut les utiliser d'une manière différente).
    - Au lieu de changer la teinte de gris d'une ligne entière, modifier que le premier pixel avec un "pixel d'index" => même problème que les variables, il ne peut y avoir que 256 lignes par défaut.
- Au lieu d'avoir des couleurs fixes par instruction, ajouter un dictionnaire de couleurs à la fin et générer le code couleurs dynamiquement.

## Sources
- https://www.sentinelone.com/blog/hiding-code-inside-images-malware-steganography/ 
# TP Compilateur

_Muller Léon_

_Campana Luca_

_Girardin Jarod_

## Introduction

Ce projet consiste à créer un compilateur personalisé, à partir d'une base produite durant le cours.

Notre programme permet de compiler un language inventé et de l'insérer dans une image, ainsi de que l'exécuter. Il est ainsi possible de faire de la stéganographie.

Notre compilateur permet de principalement analyser et exécuter des programmes "arithmétiques", ainsi que de résoudre des opérations mathématiques.

## Utilisation

    transcriptor.py {{MODE}} {{SOURCE}} {{IMAGE_SOURCE}} --debug

MODE: précise si l'action est de générer ou d'exécuter une image

    -g // générer
    -r // exécuter

SOURCE: chemin vers le code à "compiler" dans le cas d'une génération, ou le chemin vers l'image à exécuter dans le cas d'une exécution

IMAGE_SOURCE: chemin vers l'image dans laquelle il faut "compiler" le code dans le cas d'une exécution

`--debug` permet d'afficher des informations supplémentaires

_exemple_

    python transcriptor.py -g my_code.txt my_image.png
    python transcriptor.py -r code_my_image.png

## Spécifications du language

Le language supporte:
- Les variables
- Les nombres entiers
- Les chaînes de caractères (et aussi les caractères simples)
- L'arithmétique numérique
- L'arithmétique numérique avec les variables
- L'arithmétique numérique avec nombre et variable
- Les fonctions sans argument ni valeur de retour
- Les conditions IF et WHILE
    - Les conditions:
        - IF 0: FALSE
        - IF not 0: TRUE
            - ex. WHILE (x) {...} => tant que x n'est pas 0
- Le print console
- Séparation de chaque ligne par un point-virgule `;`

Les images peuvent être carrées ou rectangulaires, le nombre de pixels disponibles et nécessaires sont affichés dans la console. Dans le cas ou le nombre de pixels disponible est trop faible, la génération ne sera pas finalisée.

## Analyse lexicale

| Type d'identification | mot-clé/expréssion régulière |
| --------- | ------------------ |
| Nombres | **\d+(\.\d+)?**  |
| Caractères | **\'[\w\s]\'** |
| Chaînes de caractères | **"[\w\s]+"** |
| Type de variables | **int \| float \| double \| string** |
| Mots réservés | **while, print, if, else, function** |
| Opération arithmétique | **[+-*\^%/]** |

## Analyse syntaxique

| Type | expression |
| ---- | ---------- |
| opérations | **expression: expression ADD_OP expression \| expression MUL_OP expression \| expression MOD expression \| expression POW expression** |
| boucles | **structure: WHILE expression '{' programme '}'** |
| conditions | **structure: IF expression '{' programme '}' \| IF expression '{' programme '}' ELSE '{' programme '}'** |
| utilisation des parenthèses | **expression: '(' expression ')'**  |
| assignation | **assignation: TYPE IDENTIFIER '=' expression \| IDENTIFIER '=' expression** |
| affichage | **statement: PRINT expression** |
| nommage des fonctions | **function_name: IDENTIFIER '(' ')'** |
| déclaration de fonctions | **structure: FUNCTION function_name '{' programme '}'** |
| appel des fonctions | **structure: function_name** |
| récursivité | **programme: statement ';' programme** |

## Analyse sémantique 

### Type

Un contrôle de type est appliqué aux variables, en fonction de la valeur qui leur est affectée. Les types supportés sont: int, string, float (FIXME)

Lors des opérations arithémtiques, un contrôle de type est effectué: par exemple, si on additionne un **int** avec un **float**, un warning sera levé, mais le code compilera tout de même.

### Utilisation des fonctions et des variables

Chaque variable ou fonction définie est ajoutée à un set, si cette fonction ou variable n'est jamais utilisée un warning sera levé, mais le code compilera tout de même.

### Portée des fonctions et des variables

- Contrôle de l'utilisation ou non des variables et fonctions: par exemple, si trois variables (var0, var1 et var2) ne sont pas utilisées mais déclarées, le compilateur résumera ses variables en fin de compilation comme étant pas utilisées.

- Portée des variables : si une variable est utilisée dans un niveau plus haut que là où elle est déclarée, le programme lèvera un exception.

- Portée des fonctions : les fonctions doivent forcément être déclarée au niveau 0 (portée par défaut), et l'accès à des variables externes est impossible

## Génération de code

La génération de code se sépare en deux étapes:
- Compilation du code en [pseudo-assembleur](#pseudo-assembleur)
- Insertion du [pseudo-assembleur](#pseudo-assembleur) dans l'image

La deuxième partie diffère légèrement du cours, et est assez simple.

### Compilation du code en pseudo-assembleur

Nous avons utilisé le code svm.py fournit durant le cours, en l'adaptant à notre code.

### Insertion du pseudo-assembleur dans l'image

Le concept utilisé est le suivant: Pour chaque instruction, un **int** différent est utilisé. Chaque **int** peut être vu comme un nombre binaire. Ce nombre binaire est caché à l'intérieur des différents pixels de l'image (allant de en haut à gauche à en bas à droite: "lecture européenne").

_exemple_

Prenons une instruction simple **PRINT**, et assumons que son **int** correspondant est le **5**. Son équivalent binaire est **`101`**.

Assumons qu'il y ait 13 instructions différentes au total, chaque instruction fait donc 4 bits de long ($log_{2}{13}$ arrondi à l'entier suppérieur). Notre instruction **PRINT** est donc **`0101`**. Il faut donc la cacher sur 4 couleurs.

Chaque pixel fait 3 couleurs (RGB), l'instruction est donc cachée dans les valeurs RGB du pixel p, et dans le R du pixel p' (p et p' voir ci-dessous). Le bit de poids faible est modifié, mettons donc p et p' ayant ces valeurs par défaut:

#### Insertion dans l'image

##### p

un pixel violet-rose

- R: 1101 1110
- G: 0000 0000
- B: 1111 1111

##### p'

un pixel vert foncé

- R: 0011 1011
- G: 0111 0010
- B: 0011 1010

Après l'insertion de notre instruction, les pixels ont cette forme :

#### le nouveau pixel p

- R: 1101 111**0**
- G: 0000 000**1**
- B: 1111 111**0**

#### le nouveau pixel p'

- R: 0011 101**1**
- G: 0111 0010
- B: 0011 1010

La prochaine instruction est ajoutée à partir de la valeur G du pixel p'.

Pour les variables, les constantes, les body (pour les **GOTO**), et autre valeur "spéciale" (qui ne peut pas être écrite avec simplement une instruction), une manière équivalente est utilisée:
- Une instruction indiquant quel type de valeur à insérer est utilisé.
- Dépendant de la valeur, un certain nombre de pixels va être inséré.

_exemple_

PUSHV x

- inertion instruction PUSHV
- insertion instruction VAR
- insertion valeur de x

Pour les constantes, seul les nombre entiers sont acceptés, et leur valeur binaire est directement utilisée. Pour les variables, chaque nouvelle variable prend une nouvelle valeur.

_exemple_

```
var x = 2;
var y = 3;
var z = x+y;
```

Ici 3 variables sont utilisées, donc la logique voudrait que chaque variable fasse $log_{2}{3}$ bits.

Avec:

```
x = 00
y = 01
z = 10
```

Mais les longueurs en bit des différentes valeurs (variables, constantes, string, etc) sont définies en dur (et donc modifiables).

## Exécuter une image

L'image passée en paramètre est concidérée comme "portant du code". Si ce n'est pas le cas, une erreur est levée.

L'image est décortiquée couleur par couleur (voir [insertion de code dans image](#Insertion_dans_l_image) ci-dessus) et retransformée en [pseudo-assembleur](#pseudo-assembleur).

Une fois le [pseudo-assembleur](#pseudo-assembleur) réécrit, il est exécuté par le script _svm.py_ (donné en cours) et modifié pour correspondre à notre language.

## Pseudo-assembleur

Le fichier passé en paramètre Il est intérprété par le fichier _svm.py_ (donné en cours) et modifié pour correspondre à notre language. 

## Problèmes connus

- Analyse du type dans les opérations : il arrive que le programme ne gère pas correctement la vérification des types lors des opérations arithmétiques, notamment lorsque des boucles sont utilisées.

## Conclusion

L'ensemble des objectifs fixés ont été remplis, il est possible de compiler un programme préalablement écrit dans une image, ainsi que de l'exécuter. Le code est bien 'caché' dans l'image, et reste inchangé.

Cependant, voici quelques points qui auraient pu être ajoutés: 
- L'ajout de paramètres et la vérification de leur type dans les fonctions.
- Insertion non successive du code dans l'image de destination.
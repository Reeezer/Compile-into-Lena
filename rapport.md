# Projet Compilateur

# Compile into Lena

_Muller Léon_

_Campana Luca_

_Girardin Jarod_

## Introduction

Ce projet consiste à créer un compilateur personnalisé, à partir d'une base de code produite durant le cours.

Notre programme permet de compiler un langage inventé et de l'insérer dans une image, ainsi de que l'exécuter. Il est ainsi possible de faire de la stéganographie.

Notre compilateur permet de principalement d'analyser et exécuter des programmes "arithmétiques", ainsi que de résoudre des opérations mathématiques.

## Utilisation

```batch
    transcriptor.py {{MODE}} {{SOURCE}} {{IMAGE_SOURCE}} --debug
```

MODE: précise si l'action est de générer ou d'exécuter une image

```batch
    -g // générer
    -r // exécuter
```

SOURCE: chemin vers le code à "compiler" dans le cas d'une génération, ou le chemin vers l'image à exécuter dans le cas d'une exécution

IMAGE_SOURCE: chemin vers l'image dans laquelle il faut "compiler" le code dans le cas d'une exécution

`--debug` permet d'afficher des informations supplémentaires

_exemple_

```batch
    python transcriptor.py -g my_code.txt my_image.png
    python transcriptor.py -r code_my_image.png
```

De plus, nous avons structuré notre projet comme les TPs, il est donc possible de lancer le lexème ainsi que le parser via les fichiers lex5.py et parser5.py

Dans ce projet, il y aussi un script clean.sh permettant de nettoyer intégralement l'espace de travail afin de reprendre sur de bonnes bases les essais.

## Spécifications du langage

Le langage supporte:
- Les nombres 
- Les chaînes de caractères (et aussi les caractères simples)
- L'arithmétique numérique avec nombres et variables
- Les fonctions (sans argument ni valeur de retour)
- Les conditions IF, ELSE et WHILE
    - Les conditions:
        - IF 0: FALSE
        - IF not 0: TRUE
            - ex. WHILE (x) {...} => tant que x n'est pas 0
- Le print console
- Séparation de chaque ligne par un point-virgule (`;`)

Les images peuvent être carrées ou rectangulaires, le nombre de pixels disponibles et nécessaires est affiché dans la console. Dans le cas où le nombre de pixels disponible est trop faible, la génération ne sera pas finalisée.

## Analyse lexicale

| Type d'identification | mot-clé/expression régulière |
| --------- | ------------------ |
| Nombres | **\d+(\.\d+)?**  |
| Caractères | **\'[\w\s]\'** |
| Chaînes de caractères | **"[\w\s]+"** |
| Mots réservés | **while, print, if, else, function** |
| Opération arithmétique | **[+-*/\^%]** |

## Analyse syntaxique

| Type | expression |
| ---- | ---------- |
| opérations | **expression: expression ADD_OP expression \| expression MUL_OP expression \| expression MOD expression \| expression POW expression** |
| boucles | **structure: WHILE expression '{' programme '}'** |
| conditions | **structure: IF expression '{' programme '}' \| IF expression '{' programme '}' ELSE '{' programme '}'** |
| utilisation des parenthèses | **expression: '(' expression ')'**  |
| caractère / chaînes de caractères | **expression : CHAR \| STRING** |
| assignation | **assignation: IDENTIFIER '=' expression** |
| affichage | **statement: PRINT expression** |
| nommage des fonctions | **function_name: IDENTIFIER '(' ')'** |
| déclaration de fonctions | **structure: FUNCTION function_name '{' programme '}'** |
| appel des fonctions | **structure: function_name** |
| programme | **programme: statement ';'** |
| récursivité programme | **programme: statement ';' programme** |

## Analyse sémantique 

### Utilisation des fonctions et des variables

Chaque variable ou fonction définie est ajoutée à un set, si cette fonction ou variable n'est jamais utilisée un warning sera levé en fin de génération, mais le code compilera tout de même.

_exemple_

```
input: inputs/functionnalities/function_variable_warning.txt

a = 0;
b = 0;
c = 0;

function a(){
	z = 0;
};

function b(){
	z = 0;
};

function c(){
	z = 0;
};
```

```
output:

*** WARNING: Those functions are not used:
             - a
             - b
             - c

*** WARNING: Those variables are not used:
             - a
             - b
             - c
```

> Les variables z dans les fonctions ne sont pas marquées comme non utilisées, car les fonctions ne sont pas appelées, et on ne compile donc à aucun moment le code contenu à l'intérieur. 

### Portée des fonctions et des variables

Les variables possèdent des portées, il est donc impossible d'appeler une variable dans une portée plus basse (plus le nombre de blocs imbriqué augmente, plus le niveau est élevé) que celle où elle a été définie, auquel cas une erreur sera levée.

_exemple_

```
input: inputs/functionnalities/variable_scope.txt

if (1) {
	b = 0;
};

print b;
```

```
output:

*** ERROR: Scope is not being respected for variable 'b' in function 'main'
***        Exit code parsing
```

Les fonctions possèdent aussi une portée, il est donc impossible d'appeler une variable externe dans une fonction. 

_exemples_

```
input: inputs/functionnalities/function_scope1.txt

a = 0;

function f(){
	print a;
};

f();
```

```
output:

*** ERROR: Scope is not being respected for variable 'f_a' in function 'f'
***        Exit code parsing
```

De plus, les fonctions doivent forcément être définies au niveau le plus bas (portée par défaut).

_exemples_

```
input: inputs/functionnalities/function_scope2.txt

if (1) {
	function f(){
		a = 0;
		print a;
	};
};

f();
```

```
output:

*** ERROR: Function f has to be declared as global
***        Exit code parsing
```

### Redéfinition de fonctions

Une fonction ne peut-être définie une seconde fois.

_exemple_

```
input: inputs/functionnalities/function_override.txt

function f(){
	a = 0;
};

function f(){
	b = 0;
};
```

```
output:

*** ERROR: Function f can't be overrided
***        Exit code parsing
```

## Fonctionnalités

### Opérations arithmétiques

Certaines opérations arithmétiques ont été ajoutées par rapport au projet de base. En effet, il est maintenant possible d'effectuer un modulo, ainsi que le calcul de puissances sur des nombres.

_exemple_

```
input: inputs/functionnalities/modulo_power.txt

a = 4 % 2;
b = 5^2;

print a;
print b;
```

```
output:

0.0
25.0
```

### Gestion des chaînes de caractères

Il est possible d'assigner et d'afficher des caractères et chaînes de caractères.

```
input: inputs/functionnalities/chars_&_strings.txt

c = 'c';
str = "str";

print c;
print str;
```

```
output:

c  
str
```

### If else 

Les if, else ont été ajoutés au projet, il est donc possible d'exécuter un bloc si une condition est vraie et d'en exécuter un autre sinon.

_exemple_

```
input: inputs/functionnalities/if_else.txt

if (0){
	print 150;
} else {
	print 10;
};
```

```
output:

10.0
```

> NB: pour le if else, il faut seulement mettre un ';' à la fin du bloc complet, et non pour le if et pour le else.

### Fonctions

Il est possible de déclarer des fonctions, d'exécuter du code dedans, et de les appeler à divers endroits dans le code.

_exemple_

```
input: inputs/functionnalities/function_declaration
function aFunction() {
	print 10;
};

aFunction();
```

```
output:

10.0
```

## Génération du code intermédiaire

La génération de code se sépare en deux étapes:
- Compilation du code en [pseudo-assembleur](#pseudo-assembleur)
- Insertion du [pseudo-assembleur](#pseudo-assembleur) dans l'image

La deuxième partie diffère légèrement du cours, et est assez simple.

### Compilation du code en pseudo-assembleur

Lors de la compilation, le langage créé est directement transformé en code pseudo-assembleur, qui sera par la suite transformé en bits afin d'être "caché" dans le code RGB d'une image.

### Insertion du pseudo-assembleur dans l'image

Le concept utilisé est le suivant: pour chaque instruction, un **int** différent est utilisé. Chaque **int** peut être vu comme un nombre binaire. Ce nombre binaire est caché à l'intérieur des différents pixels de l'image (allant d’en haut à gauche à en bas à droite: "lecture européenne").

_exemple_

Prenons une instruction simple **PRINT**, et assumons que son **int** correspondant est le **5**. Son équivalent binaire est **`101`**.

Assumons qu'il y ait 13 instructions différentes au total, chaque instruction fait donc 4 bits de long ($log_{2}{13}$ arrondi à l'entier supérieur). Notre instruction **PRINT** est donc **`0101`**. Il faut donc la cacher sur 4 couleurs.

Chaque pixel fait 3 couleurs (RGB), l'instruction est donc cachée dans les valeurs RGB d'un premier pixel p, et dans le R d'un second pixel p' (p et p' voir ci-dessous). Le bit de poids faible est modifié, mettons donc p et p' ayant ces valeurs par défaut:

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

La prochaine instruction est donc ajoutée à partir de la valeur G du pixel p'.

Pour les variables, les constantes, les body (pour les **GOTO**), et autre valeur "spéciale" (qui ne peut pas être écrite avec une seule instruction), une manière équivalente est utilisée:
- Une instruction indiquant quel type de valeur à insérer est utilisé.
- Dépendant de la valeur, un certain nombre de pixels va être inséré.

_exemple_

PUSHV x

- insertion instruction PUSHV
- insertion instruction VAR
- insertion valeur de x

Pour les constantes, seuls les nombres entiers sont acceptés (en réalité les nombres flottants sont acceptés, mais castés en int par la suite), et leur valeur binaire est directement utilisée. Pour les variables, chaque nouvelle variable prend une nouvelle valeur.

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

Mais les longueurs en bit de différentes valeurs (variables, constantes, string, etc) sont définies en dur ce qui veut dire que dans l'état par exemple il n'est possible d'avoir un nombre que contenu entre -255 et 255.

## Exécuter une image

L'image passée en paramètre est considérée comme "portant du code correct". Si ce n'est pas le cas, une erreur est levée.

L'image est décortiquée couleur par couleur (voir [insertion de code dans image](#Insertion_dans_l_image) ci-dessus) et retransformée en [pseudo-assembleur](#pseudo-assembleur).

Une fois le [pseudo-assembleur](#pseudo-assembleur) réécrit, il est exécuté par le script _svm.py_ (donné en cours) et modifié pour correspondre à notre langage (PUSHS, MOD, POW, PASS).

## Problèmes connus

### Chaînes de caractères

L'arithmétique des chaînes de caractères n'est pas supportée.

_exemple_

```
input: inputs/functionnalities/string1.txt

s1 = "s1";
s2 = "s2";
s3 = s1+s2;
print s3;
```

```
output:

s1s2
```

L'arithmétique des chaînes de caractères avec des nombres n'est pas supportée.

_exemple_

```
input: inputs/functionnalities/string1.txt

s1 = "s1";
i1 = 3;

mixed = s1+i1;
print mixed;
```

```
output:

TypeError: can only concatenate str (not "float") to str
```

### Nombre flottant

Les nombres flottants ne sont pas supportés

L'idée est d'utiliser les fonctions _floatToBits_ et _bitsToFloat_ afin de transformer le nombre flottant en nombre entier, pour ensuite le stocker en binaire, lors de l'exécution de faire l'inverse (binaire -> entier -> flottant).

Le problème est que lorsque nous avons ajouté cette fonctionnalité, toutes les autres ne fonctionnent plus.

Cela demanderait du temps en debug, mais nous préférons rendre un projet testé et fonctionnel seulement "fonctionnel en théorie".

## Conclusion

L'ensemble des objectifs fixés ont été remplis, en effet il est possible de compiler un programme (préalablement écrit) et de l'insérer dans une image, ainsi que de l'exécuter. Le code est bien 'caché' dans l'image, et reste inchangé.

Cependant, voici quelques points qui auraient pu être ajoutés: 
- L'ajout de paramètres et la vérification de leur type dans les fonctions.
- Le retour de variables dans les fonctions.
- Insertion non successive du code dans l'image de destination.
- Ajout des nombres flottants (voir [nombres flottants](#nombres-flottants))
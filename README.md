# Project : Abstract Argumentation Solver

Le but de ce projet est de pouvoir lire des fichier du type `.apx` contenant des représentations textuelles de graph. De parser ces fichiers pour créer les graphs, puis de résoudres des problèmes d'argumentation à partir de ces graphs.

Les problèmes sont les suivants :
 - `VE-CO`: Vérifier si une extension donnée est complète.<br>
 **Args** : un enssemble de point du graph.


 - `DC-CO`: Vérifier si un argument appartient à au moins une extension complète. <br>
 **Args** : un ou plusieurs point(s) du graph.


 - `DS-CO`: Vérifier si un argument appartient à toutes les extension complète.<br>
 **Args** : un ou plusieurs point(s) du graph.


 - `VE-ST`: Vérifier si une extension donnée est stable.<br>
 **Args** : un enssemble de point du graph.

 - `DC-ST`: Vérifier si un argument appartient à au moins une extension stable.<br>
 **Args** : un ou plusieurs point(s) du graph.<br>

 - `DS-ST`: Vérifier si un argument appartient à toutes les extension stable.<br>
 **Args** : un ou plusieurs point(s) du graph.


**Notez** que pour les problèmes autres que `VE-ST` et `VE-CO`, utiliser plusieurs arguments vérifie juste que le problème est vrai pour chacun. 

Par exemple `python3 main.py -p DC-ST -f test/test_af1.apx -a a,b` vérifie que `b`  **ET**  `a` (séparément) appartienent tous deux à **au moins** une des **extensions stables** du graph. Cela équivaudrait à tester `a` et `b` séparément et d'effectuer un et logique entre les deux résultats.

## Exécution

Pour éxécuter le programme voici la commande de base:
`python3 main.py -p [PROB] -f [FILE] -a [ARGS]`
#### Liste des options :
 - **-p  [PROB]** : `PROB` est le problème choisi.
 - **-f  [FILE]** : `FILE` est le chemin vers le fichier contenant le graph choisi.
 - **-a  [ARGS]** : `ARGS` le ou les arguments à fournir pour le problème.
 - **-h, --help** : Affiche le menu d'aide contenant toutes les commandes et leurs utilisations
 - **-d, --debug** : Affiche le mode debug contenant le graph, le powerset, les extensions admissibles, complètes et stables.


## Cœur du projet
### Le parsing
Pour parser les fichier `.apx` on utilise la bibliothèque `re` afin d'utiliser la regex suivante `(arg|att)\(([A-Z](,[A-Z])*)`. Si on la décompose cette regex vient dans un premier temps détecter soit `arg` soit `att` puis une parenthèse `\(` suivie d'une (`[A-Z]`) ou plusieures lettres majuscules séparées par une virgule `(,[A-Z])*`.

```python
if typ == "arg":
    graph[point] = set()
elif typ == "att":
    graph[point[0]].add(point[-1])
```
Pour la représentation du graph on utilise un dictionnaire dont les clés sont les points et les valeurs des ensembles d'attaques. Pour chaque match de la **regex**, si le type est `arg` on ajoute une nouvelle entrée dans le dictionnaire avec pour clé un `set` vide, tandis que si le type est `att` on ajoute l'attaque dans le `set`.

### Création du powerset
Pour trouver les extensions du graph on génère un powerset (ensemble de tous les ensembles possibles). Pour cela on utilise `combination` de la bibliothèque `itertools` qui, pour une liste et une taille `x` données renvoie toutes les combinaisons de taille `x`.
```python
return [s for x in range(len(keys)+1) for s in list(combinations(keys, x))]
```
Exemple pour un graph à trois points (A,B,C) :
>[(), ('A',), ('B',), ('C',), ('A', 'B'), ('A', 'C'), ('B', 'C'), ('A', 'B', 'C')]

### Sous graphe
Afin de récupérer facilement les attaques/défenses d'un ensemble d'argument. On utilise la fonction `get_subgraph()` qui permet de récupérer une partie du graph :
```python
{k:v for k,v in graph.items() if k in arg_set}
```
En l'occurence on ne récupère que les point présent dans l'ensemble d'argument mis en paramètre.

### La défense
Pour commencer à trouver toutes les extensions, il est nécessaire de créer une fonction permettant de vérifier si un argument est défendu. Pour cela on utilise la fonction `is_defended()`. La fonction prend en paramètre un `graph`, un ensemble d'arguments `arg_set` et un argument `arg` et qui vérifie si l'argument est défendu par au moins un membre de l'ensemble d'argument.
```python
attacker = [k for k,v in graph.items() if arg in v]
for a in arg_set:
    attacker = [x for x in attacker if x not in graph[a]]
return not attacker
```
Pour cela on ajoute dans une liste `attacker` tous les point du graph qui attaquent `arg`. Par la suite on retire de cette liste les point qui sont attaqué à leur tour par un membre de `arg_set`. Enfin on retourne si la liste est vide ou non.

<!-- is_defended(graph: dict, arg_set:set, arg:str)                               
is_admissible(graph: dict, arg_set: set)
is_complete(graph: dict, arg_set: set)
is_stable(graph: dict, arg_set: set)
class HandleException(Exception)
handle_entries() -->


<!-- ### Road Map
- [x] Ecriture de message  -->



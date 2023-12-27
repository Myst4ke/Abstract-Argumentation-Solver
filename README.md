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

### Extension admissible
Pour détecter les extensions adissibles on utilise la fonction `is_admissible()` prennant en paramètre  un `graph` et un ensemble d'argument `arg_set` (extension). La fonction vérifie si l'extension donnée est sans conflit et qu'elle défend ses membres.<br>
**Sans conflit :**
```python
sub_graph = get_subgraph(graph, arg_set)
for elem in arg_set:
    for _, values in sub_graph.items():
        if elem in values:
            return False
```
Afin de detecter les conflit parmis l'extension on récupère le `sub_graph` pour obtenir facilement les attaques de tous les arguments. Par la suite on itère dans le `sub_graph` afin de vérifier qu'un membre de l'extension ne s'y trouve pas.<br><br>
**Défense :**
```python
return all(is_defended(graph, arg_set, arg) for arg in arg_set)
```
Si aucun conflit n'est détecté on utilise la fonction `is_defended()` définie plus tôt pour vérifier que tous les membres de l'extension sont défendus par au moins un autre membre de cette extension.

### Extension complète
Pour détecter les extensions complètes on utilise la fonction `is_complete()` prennant en paramètre  un `graph` et un ensemble d'argument `arg_set`. 
```python
if is_admissible(graph, arg_set):
    defended_args = {key for key in graph.keys() if is_defended(graph, arg_set, key)}
    return defended_args == arg_set
return False
```
On vérifie dans un premier temps que l'extension est bien admissible grâce à `is_admissible()`. Puis pour tous les points du graph on les ajoute à un ensemble (`defended_args`) si ils sont défendus par l'extension passée en paramètre. Pour finir on compare `defended_args` à notre extension `arg_set` afin de vérifier que les arguments défendus sont bien tous dans l'extension.

### Extension stable
Afin détecter les extensions stables on utilise la fonction `is_stable()` prennant en paramètre  un `graph` et un ensemble d'argument `arg_set`. 
```python
sub_graph = get_subgraph(graph, arg_set)
if is_complete(graph, arg_set):
    should_attack = {x for x in graph.keys() if x not in arg_set}
    attacking = {x for sublist in sub_graph.values() for x in sublist}
    return attacking == should_attack
return False
```
Pour cela on créé le `sub_graph` grâce à la fonction `get_subgraph` afin d'obtenir les attaques de l'extension. On vérifie qu'elle est complète dans un premier temps, puis on récupères l'ensemble des points du graph n'éttant pas dans l'extension et on les compare au attaques de l'extension pour vérifier qu'elle attaque bien tout ce qu'elle ne contient pas.

### La gestion des commandes
Comme demandé il fallait être capable de gérer les options d'exécution `-p`, `-f` et `-a` à celles la nous avons décidé de rajouter un mode debug utilisable avec `-d` ou `--debug` et un menu d'aide affichable avec `-h` ou `--help`. Pour la gestion des commandes on utilise les bibliothèque `sys` et surtout `getopt` qui permet une meilleure gestion des arguments en ligne de commande que `sys` utilisée toute seule. 

La fonction `getopt()` permet de prendre en argument des nom de commande et de renvoyer les arguments correspondants en ligne de commande.
```python
getopt.getopt(sys.argv[1:] , "p:f:a:dh",["debug", "help"])
```
**Notez** qu'il faut bien sur lui passer en paramètre la liste des arguments présent en ligne de commande.

Pour faciliter la gestion des erreurs on utilise une classe `HandleException` héritée de la classe `Exception` permettant d'améliorer la lisibilité du code.
```python
class HandleException(Exception):...
```

La gestion des commandes s'effectue dans une fonction appelée `handle_entries()`. La fonction s'éxécute de la manière suivante
```python
try:
        # Récupération des commandes et des arguments
        opts = dict(go.getopt(sys.argv[1:] , "p:f:a:dh",["debug", "help"])[0]) 
        try:
            # Présence ou non de certaines commandes ...

            # Raise une HandleException si elles ne sont pas présentes
            
            # Match sur les différent problèmes
                match opts["-p"]:
                    case "VE-CO":...
                    case "DC-CO":...
                    case "DS-CO":...
                    case "VE-ST":...
                    case "DC-ST":...
                    case "DS-ST":...
                    case _:
                        raise HandleException("This mode is unknown.")
        
        except HandleException as h:
            print(h, "Try using --help,-h")
        except Exception as e:
            print(e)
    # Erreur lors de la présence d'une commande inconnue
    except go.GetoptError as e: 
        print(f"`-{e.opt}` option is unknown.", "Try using --help,-h")
```
Les lignes de commandes peuvent donc être écrite dans n'importe quel ordre tant que les options principales sont présentes. Elles peuvent même contenir du texte inutile à la fin. 

**Exemples :**
 - la commande `python3 main.py -a d,b -dp DS-ST -f test/test_af5.apx ` est valide.
 - la commande `python3 main.py -dp DS-ST -f test/test_af5.apx -a d,b TexteQuiNaRienAfaireLà` est valide.

### Conclusion
Le programme fourni permet de résoudre différents problèmes d'argumentation sur des graph lu et créés depuis des fichiers. Il utilise une méthode exhaustive visant à créer toutes les extensions possibles (`powerset`) et à ne garder que celles répondant au différent prédicats (`is_admissible()`,`is_complete()`, `is_stable()`).



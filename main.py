import re
from itertools import combinations
import sys
from getopt import getopt

def graph_from_file(filename: str) -> dict:
    """ reads an .apx file and return the according graph """
    with open(filename, 'r') as f:
        content = f.read()
    
    patterns = re.findall(r'(arg|att)\(([A-Z](,[A-Z])*)', content)

    graph = {}
    for pat in patterns:
        # unpacking pat (re.Match)
        typ, point, *_ = pat  # typ = "arg" or "att", point = [A-Z] or [A-Z],[A-Z]
        if typ == "arg":
            graph[point] = []
        elif typ == "att":
            graph[point[0]].append(point[-1])
    return graph


def create_powerset(keys: list|set) -> list[tuple]:
    """ Return all set possible from a given list/set """
    return [s for x in range(len(keys)+1) for s in list(combinations(keys, x))]


def get_subgraph(graph: dict, arg_set: set):
    """ Return a mapping of a graph based on the keys passed as `arg_set` """
    return {k:v for k,v in graph.items() if k in arg_set}


def is_defended(graph: dict, arg_set:set, arg:str) -> bool:
    """ Check whether arg is defended by any of arg_set member """
    attacker = [k for k,v in graph.items() if arg in v]
    for a in arg_set:
        attacker = [x for x in attacker if x not in graph[a]]
    return not attacker


def is_admissible(graph: dict, arg_set: set) -> bool:
    """ Check if a set of args is an admissible extension of graph """

    # Conflict-freeness
    sub_graph = get_subgraph(graph, arg_set)
    for elem in arg_set:
        for _, values in sub_graph.items():
            if elem in values:
                return False
            
    # Defense
    for arg in arg_set:
        if not is_defended(graph, arg_set, arg):
            return False
        
    return True


def is_complete(graph: dict, arg_set: set) -> bool:
    """ Check if `args_set` is a complete extension of `graph` """
    defended_args = []
    if is_admissible(graph, arg_set):
        for key in graph.keys():
            if is_defended(graph, arg_set, key): # Get all the defended args of the arg_set
                defended_args += key

    return set(defended_args) == arg_set


def is_stable(graph: dict, arg_set: set) -> bool:
    """ Check if `args_set` is a stable extension of `graph` """
    if is_admissible(graph, arg_set):
        sub_graph = get_subgraph(graph, arg_set)
        should_attack = [x for x in graph.keys() if x not in arg_set]
        attacking = [x for sublist in sub_graph.values() for x in sublist]
        return set(attacking) == set(should_attack)
    return False


def handle_entries():
    """ Handle every args from the execution command line """
    # Get all the options from command line
    opts = dict(getopt(sys.argv[1:] , "p:f:a:d",["debug"])[0]) 
    
    graph = graph_from_file(opts["-f"])
    powerset = create_powerset(graph.keys())
    admissible = [x for x in powerset if is_admissible(graph, set(x)) ]
    complete = [x for x in powerset if is_complete(graph, set(x))]
    stable = [x for x in powerset if is_stable(graph, set(x))]

    if "-p" in opts.keys():
        points = opts["-a"].upper().split(",")

        match opts["-p"]:
            case "VE-CO":
                return is_complete(graph, set(points))

            case "DC-CO":
                for elem in complete:
                    if points in elem:
                        return True
                return False
            
            case "DS-CO":
                for elem in complete:
                    if not points in elem:
                        return False
                return True
            
            case "VE-ST":
                return is_stable(graph, set(points.split(",")))
            
            case "CD-ST":
                for elem in stable:
                    if points in elem:
                        return True
                return False
            
            case "DS-ST":
                for elem in stable:
                    if not points in elem:
                        return False
                return True
            
            case _:...

    elif "-d" or "--debug" in opts.keys():
        print("Graph :\n",graph, end="\n\n")
        print("Powerset :\n",powerset, end="\n\n")
        print("All admissible extensions :\n",admissible, end="\n\n")
        print("All complete extensions :\n", complete, end="\n\n")
        print("All stable extensions :\n", stable)
        return -1 # Instead of returning `None` wich would result in printing `NO`
            

def main():
    if (output := handle_entries()) != -1:
        if output:
            print("YES")
        elif not output:
            print("NO")
    
    
if __name__ == "__main__":
    main()
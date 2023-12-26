import re
import sys
import os # used for terminal size
import getopt as go
from itertools import combinations # Used to create powerset

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
            graph[point] = set() # Set instead of list to keep uniqueness among attacks
        elif typ == "att":
            graph[point[0]].add(point[-1])
    
    return graph


def create_powerset(keys) -> list[tuple]:
    """ Return all set possible from a given list/set """
    return [s for x in range(len(keys)+1) for s in list(combinations(keys, x))]


def get_subgraph(graph: dict, arg_set: set):
    """ Return a mapping of a graph based on the keys passed as `arg_set` """
    return {k:v for k,v in graph.items() if k in arg_set}


def is_defended(graph: dict, arg_set:set, arg:str) -> bool:
    """ Check whether `arg` is defended by any of `arg_set` member """
    attacker = [k for k,v in graph.items() if arg in v]
    for a in arg_set:
        attacker = [x for x in attacker if x not in graph[a]]
    return not attacker


def is_admissible(graph: dict, arg_set: set) -> bool:
    """ Check if a `arg_set` is an admissible extension of `graph` """

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

# Created to make handleling errors a bit cleaner
class HandleException(Exception):...

def handle_entries():
    """ Handle every args from the execution command line """
    try:
        # Get all the options from command line
        opts = dict(go.getopt(sys.argv[1:] , "p:f:a:dh",["debug", "help"])[0]) 
        # print(opts)
        try:
            
            # Help Menu
            if "-h" in opts.keys() or "--help" in opts.keys():
                    printing = f"\033[1m Help menu\033[0m".center(os.get_terminal_size()[0])+"\n\n" # Centered on terminal width, bold txt
                    printing += "Usage : python3 main.py -p [param] -f [filepath] -a [args]\n"
                    printing += "Options:\n"
                    printing += "\t\033[1m-p [param]\033[0m : Solves the param given. Can choose between [VE-CO, DC-CO, DS-CO, VE-ST, DC-ST, DS-ST]\n"
                    printing += "\t\033[1m-f [filepath]\033[0m : Uses the file as input file for the graph. Must be a `.apx` type of file !\n"
                    printing += "\t\033[1m-a [args]\033[0m : Uses args as a set for the param solver.\n"
                    printing += "\t\033[1m-d, --debug\033[0m : Print graph, powerset, admissible extensions, complete extensions and stable extensions.\n"
                    printing += "\t\033[1m-h, --help\033[0m : Print out the help menu.\n\n"
                    printing += "Debug usage : python3 main.py -d -f [filepath]\n"
                    printing += "\x1B[3m*Note that options can be passed in any order*\x1B[0m"
                    print(printing)
                    return -1

            if "-f" not in opts.keys():
                raise HandleException("No file supplied, use -f to supply file")
            else:
                graph = graph_from_file(opts["-f"])
                powerset = create_powerset(graph.keys())
                admissible = [x for x in powerset if is_admissible(graph, set(x))]
                complete = [x for x in powerset if is_complete(graph, set(x))]
                stable = [x for x in powerset if is_stable(graph, set(x))]

                if "-d" in opts.keys() or "--debug" in opts.keys(): # -d has to be used with -f
                    print("Graph :\n",graph, end="\n\n")
                    print("Powerset :\n",powerset, end="\n\n")
                    print("All admissible extensions :\n",admissible, end="\n\n")
                    print("All complete extensions :\n", complete, end="\n\n")
                    print("All stable extensions :\n", stable)
                
                if "-p" not in opts.keys():
                    raise HandleException("Missing parameters, use -p to suplly parameters")
                else:
                    if "-a" not in opts.keys():
                        raise HandleException("No argument supplied. Use -a to supply args")
                    else:
                        points = opts["-a"].upper().split(",")
                        # Checks if all supplied args are in the graph.keys()
                        if not all(x in graph.keys() for x in points): 
                            raise HandleException("Some arguments are not part of the supplied graph.")
                        else:
                            match opts["-p"]:
                                case "VE-CO":
                                    return is_complete(graph, set(points))

                                case "DC-CO": # Can be used with multiple args
                                    # Checks whether all supplied args belongs to at least one complete extension
                                    return all(any(point in elem for elem in complete) for point in points)
                                
                                case "DS-CO":
                                    return all(point in elem for elem in complete for point in points)
                                
                                case "VE-ST":
                                    return is_stable(graph, set(points))
                                
                                case "DC-ST": # Can be used with multiple args
                                    # Checks whether all supplied at least args belongs to one stable extension
                                    return all(any(point in elem for elem in stable) for point in points)
                                
                                case "DS-ST":
                                    return all(point in elem for elem in stable for point in points)
                                
                                case _:
                                    raise HandleException("This mode is unknown.")
                    
        
        except HandleException as h:
            print(h, " Try using --help,-h")
            return -1 # Instead of returning `None` wich would result in printing `NO` (False == None)
        except Exception as e:
            print(e)
            return -1

    except go.GetoptError as e:
        print(f"`-{e.opt}` option is unknown ")
        return -1

def main():
    # print(dict(getopt(sys.argv[1:] , "p:f:a:dh",["debug"])[0]) )
    if (output := handle_entries()) != -1:
        if output:
            print("YES")
        elif not output:
            print("NO")
    
    
if __name__ == "__main__":
    main()
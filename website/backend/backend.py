from typing import Optional, List, Tuple
from flask import session, flash
from website.backend.variables import *
from website.backend.functions import *

class Node:
    def __init__(self, value="", previous=None, next=None):
        self.value = value
        self.previous = previous
        self.next = next


def CountArguments(function_str: str) -> int:
    """
        This function counts the number of arguments a function has.
    Args:
        function_str (str): the remainder of the input string after the function character was found

    Returns:
        int: number of arguments this function has. returns -1 if it's an invalid string
    """
    arguments = 1
                    
    open_brackets = 1
    i = 0
    while (i < len(function_str) and open_brackets > 0):
        i += 1
        if function_str[i] == "," and open_brackets == 1: # we're accepting another argument for this function
            arguments += 1
        elif function_str[i] == "(":
            open_brackets += 1
        elif function_str[i] == ")":
            open_brackets -= 1
            
    return arguments if open_brackets == 0 else -1


def LoadLanguage(input_str: str) -> None:
    """
        This function takes in a string argument and loads the 
        found functions and variables into their respective objects.
    Args:
        input_str (str): term to load the language from
    """
    functions = {}
    variables = set([])
    
    i = 0
    while i < len(input_str):
        if input_str[i] not in "(), ":
            term = input_str[i]
            while i + 1 < len(input_str) and input_str[i + 1] not in "(), ":
                i += 1
                term += input_str[i]
            
            check = i
            while check + 1 < len(input_str) and input_str[check + 1] == " ":
                check += 1
                pass
                
            if i + 1 == len(input_str): # this should just be an atomic variable
                if len(variables) + len(functions) == 0: # this should be the ONLY term
                    variables.add(term)
                else:
                    flash("ERROR: String invalid. It ends with a term, but it's not an atomic term.", category='error')
                    return
            
            if check != i and input_str[check + 1] not in ",)":
                flash("ERROR: You either need a comma between variables in the same function or to close the function.", category="error")
                return
                
            if term not in variables and term not in functions:
                if input_str[i + 1] == "(": # this has to be a function accepting at least one argument
                    functions[term] = CountArguments(input_str[i + 1:])
                    
                    if functions[term] == -1:
                        flash("ERROR: String is invalid, couldn't determine number of arguments for function {term}!", category='error')
                        return
                else: # this is either a constant or a variable. No way to tell, so we're just putting it as a variable for now
                    variables.add(term)
            elif term in functions: 
                if input_str[i + 1] == "(": # this has to be a function accepting at least one argument
                    arguments = CountArguments(input_str[i + 1:])
                    
                    if arguments != functions[term]:
                        flash(f"ERROR: Function {term} found again, taking a different number of arguments than before! \
                                Found {functions[term]} before, now found {arguments}.", category='error')
                        return
        
        i += 1
    
    session["functions"] = functions
    session["variables"] = list(variables) # sets aren't JSON serializable


def CreateTree(input_str: str) -> Optional[Node] :
    """
        This function takes in a string argument and returns the corresponding 
        tree, if it can be created. It will otherwise return None.
    Args:
        input_str (str): term to create the tree from

    Returns:
        Optional[Node]: returns the head of the tree or None if it can't be created
    """
    
    functions = session["functions"] if "functions" in session else {}
    variables = session["variables"] if "variables" in session else set([]) # sets aren't JSON serializable
    
    head = Node()
    current_node = head
    
    for i in range(len(input_str)):
        str = input_str[i]
        
        if str not in "(), ":
            while i + 1 < len(input_str) and input_str[i + 1] not in "(), ":
                i += 1
                str += input_str[i]
        
        if str in functions.keys(): # if current char represents a function
            if current_node.value != "":
                flash("ERROR: More than one function is trying to occupy the same node!", category='error')
                return None
            current_node.value = str # first we note this down
            
            if functions[str] > 0:
                current_node.next = [] # we prepare a list of Nodes if the function takes more than zero arguments

                for _ in range(0, functions[str]): # then we add as many further Nodes as the function has possible arguments
                    current_node.next.append(Node(previous=current_node))
        elif str == '(':
            if current_node.next == None:
                flash("ERROR: There's an open paranthesis, but we're not expecting any arguments!", category='error')
                return None
            
            current_node = current_node.next[0] # we go in the first Node in the list of children of the current one
        elif str == ')':
            if current_node.previous == None:
                flash("ERROR: There are too many closed parantheses!", category='error')
                return None
            
            if current_node.next != None:
                for node in current_node.next:
                    if node.value == "":
                        flash("ERROR: Function is still expecting arguments!", category='error')
                        return None
            
            if current_node.value == "":
                flash("ERROR: Function is still expecting arguments!", category='error')
                return None
            
            current_node = current_node.previous # we jump one level above our current one
        elif str == ',':
            if current_node.previous == None: # if there is no higher level to jump to
                flash("ERROR: Too many commas!", category='error')
                return None
            
            current_node = current_node.previous # we need to jump a level up
            initial_node = current_node
            for node in current_node.next: # look for a Node which hasn't been populated yet
                if node.value == "":
                    current_node = node
                    break
                
            if current_node == initial_node: # we couldn't find an unpopulated Node
                flash("ERROR: Function given more arguments than it can accept!", category='error')
                return None
        elif str in variables:
            if current_node.value != "":
                flash("ERROR: More than one variable is trying to occupy the same node!", category='error')
                return None
            
            current_node.value = str

    return head


def PrintTreeNode(head: Node, spacing: int = 2, current_level: int = 0) -> str:
    """
    This function takes in the head of a tree and prints the content out to the console.

    Args:
        head (Node): head of the tree you want to display
        spacing (int): how many whitespaces and dash characters should be used when displaying a new line (has to be > 0)
        current_level (int): the current level of the tree (this shouldn't be given as a parameter on the first call)

    Returns:
        str: returns the list representation as a string
    """
    tree_repr = ""
    
    if spacing <= 0:
        raise ValueError("spacing must be greater than 0")

    stack = [(head, current_level, "0")]
    while stack:
        node, level, node_pos = stack.pop()

        if node == None:
            flash("ERROR: Could not create tree.", category="error")
            return
        
        tree_repr += (' ' * (spacing + 1) * (level - 1) + ('+' + '-' * spacing) * (level > 0) + node.value) + \
                        (f" ({node_pos})" if node != head else "") + '\n'

        if node.next != None:
            node_pos += "_0" if node != head else ""
            for child in node.next:  # Iterate through children
                node_pos = node_pos[:node_pos.rfind("_") + 1] + str(int(node_pos[node_pos.rfind("_") + 1:]) + 1)
                stack.append((child, level + 1, node_pos))
                
            stack[len(stack) - len(node.next):] = reversed(stack[len(stack) - len(node.next):])
        
    return tree_repr
    

def GetSubtermAtPosition(position: str, term: List) -> List:
    """
    This function takes in a position from the term and returns the subterm from
    that position onward.

    Args:
        node (Node): node of the term you want to change the data structure of
        term (List): list representing a term

    Returns:
        List: returns the list of lists or [] if there's an error
    """
    pass
    

def AppendChildrenNodesToList(node: Node) -> List:
    """
    This function takes in a node of a tree and returns the contents
    of its children within a list of lists.

    Args:
        node (Node): node of the term you want to change the data structure of

    Returns:
        List: returns the list of lists or [] if there's an error
    """
    list = []
    
    for child in node.next:
        list.append(child.value)
        
        if child.next != None:
            list.append(AppendChildrenNodesToList(child))
        
    return list
    

def ChangeTreeToList(head: Node) -> List:
    """
    This function takes in the head of a tree and returns the contents within a list of lists.

    Args:
        head (Node): head of the term you want to change the data structure of

    Returns:
        List: returns the list of lists or [] if there's an error
    """
    list = []
    
    if head == None:
        return list
    
    list.append(head.value)
    
    list.append(AppendChildrenNodesToList(head))
    
    return list


def AppendChildrenToNode(term: List, current_node: Node) -> None:
    """
    This function takes in a sublist of a list and returns the contents
    of its children within a tree structure.

    Args:
        term (List): sublist of the term you want to change the data structure of

    Returns:
        Optional[Node]: returns the tree structure or [] if there's an error
    """
    # ['f1', ['f2', ['i1', ['e'], 'i', ['f', ['x', 'y']]], 'i', ['f', ['i', ['x'], 'y']]]]
    if len(term) == 1:
        current_node.value = term[0]
        return
    
    child_index = 0
    
    for elem in term:
        if type(elem) == list:
            if current_node.next == None:
                flash("ERROR: There isn't a Node to continue forward with the list!", category="error")
                return
            
            if child_index == len(current_node.next):
                flash("ERROR: This function can't accept any more children!", category="error")
                return
            
            AppendChildrenToNode(elem, current_node.next[child_index])
            child_index += 1
        else:
            if current_node.next == None:
                current_node.next = []
            
            current_node.next.append(Node(value = elem, previous = current_node))


def ChangeListToTree(term: List) -> Optional[Node]:
    """
    This function takes in a list of lists and returns the contents within the form of a tree.

    Args:
        term (List): the list of lists representing a term

    Returns:
        Optional[Node]: returns the head of the tree or None if there's an error
    """
    if term == []:
        flash("ERROR: Can't take in an empty list!", category="error")
        return None
    
    head = Node(term[0])
    AppendChildrenToNode(term[1], head)
    
    return head


def LoadTerm(name: str) -> Optional[Tuple[str, List]]:
    """
    This function takes in the head of a tree and returns the contents within a list of lists.

    Args:
        name (str): the name by which to remember this term

    Returns:
        Optional[Tuple[str, List]]: returns a tuple with the string representation 
        and the list of lists or None if there's an error
    """
    term_dictionary = session["terms"] if "terms" in session else {}
    
    if name not in term_dictionary:
        flash(f"ERROR: No term with the name {name} found in the dictionary!", category="error")
        return None
    
    return term_dictionary[name]


def SaveTerm(term: List, input_str: str, name: str) -> None:
    """
    This function saves the current term to the user session for later use
    in the format (string_representation, list_representation)

    Args:
        term (List): list of lists representing a term
        input_str (str): stromg representation of the term
        name (str): the name by which to remember this term
    """
    term_dictionary = session["terms"] if "terms" in session else {}
    
    term_dictionary[name] = (input_str, term)
    
    session["terms"] = term_dictionary

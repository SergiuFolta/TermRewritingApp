from typing import Optional, List
from flask import session, flash

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
                
            if i + 1 == len(input_str): # this should just be an atomic variable
                if len(variables) + len(functions) == 0: # this should be the ONLY term
                    variables.add(term)
                else:
                    flash("ERROR: String invalid. It ends with a term, but it's not an atomic term.", category='error')
            
            if term not in variables and term not in functions:
                if input_str[i + 1] == "(": # this has to be a function accepting at least one argument
                    functions[term] = CountArguments(input_str[i + 1:])
                    
                    if functions[term] == -1:
                        flash("ERROR: String is invalid, couldn't determine number of arguments for function {term}!", category='error')
                else: # this is either a constant or a variable. No way to tell, so we're just putting it as a variable for now
                    variables.add(term)
            elif term in functions: 
                if input_str[i + 1] == "(": # this has to be a function accepting at least one argument
                    arguments = CountArguments(input_str[i + 1:])
                    
                    if arguments != functions[term]:
                        flash(f"ERROR: Function {term} found again, taking a different number of arguments than before! \
                                Found {functions[term]} before, now found {arguments}.", category='error')
        
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
                flash("Error in string! More than one function is trying to occupy the same node!", category='error')
                return None
            current_node.value = str # first we note this down
            
            if functions[str] > 0:
                current_node.next = [] # we prepare a list of Nodes if the function takes more than zero arguments

                for _ in range(0, functions[str]): # then we add as many further Nodes as the function has possible arguments
                    current_node.next.append(Node(previous=current_node))
        elif str == '(':
            if current_node.next == None:
                flash("Error in string! There's an open paranthesis, but we're not expecting any arguments!", category='error')
                return None
            
            current_node = current_node.next[0] # we go in the first Node in the list of children of the current one
        elif str == ')':
            if current_node.previous == None:
                flash("Error in string! There are too many closed parantheses!", category='error')
                return None
            
            if current_node.next != None:
                for node in current_node.next:
                    if node.value == "":
                        flash("Error in string! Function is still expecting arguments!", category='error')
                        return None
            
            current_node = current_node.previous # we jump one level above our current one
        elif str == ',':
            if current_node.previous == None: # if there is no higher level to jump to
                flash("Error in string! Too many commas!", category='error')
                return None
            
            current_node = current_node.previous # we need to jump a level up
            initial_node = current_node
            for node in current_node.next: # look for a Node which hasn't been populated yet
                if node.value == "":
                    current_node = node
                    break
                
            if current_node == initial_node: # we couldn't find an unpopulated Node
                flash("Error in string! Function given more arguments than it can accept!", category='error')
                return None
        elif str in variables:
            if current_node.value != "":
                flash("Error in string! More than one variable is trying to occupy the same node!", category='error')
                return None
            
            current_node.value = str

    return head


def PrintTreeNode(head: Node, spacing: int = 2, current_level: int = 0) -> None:
    """
    This function takes in the head of a tree and prints the content out to the console.

    Args:
        head (Node): head of the tree you want to display
        spacing (int): how many whitespaces and dash characters should be used when displaying a new line (has to be > 0)
        current_level (int): the current level of the tree (this shouldn't be given as a parameter on the first call)
    """
    print(' ' * (spacing + 1) * (current_level - 1) + ('+' + '-' * spacing) * (current_level > 0) + head.value)
    
    if head.next == None: # no more children to look into
        return
    
    for node in head.next:
        PrintTreeNode(node, spacing, current_level + 1)
        
        
def PrintTreeList(term: List, spacing: int = 2, current_level: int = 0) -> None:
    """
    This function takes in a list representing a term and prints the content out to the console.

    Args:
        term (List): head of the tree you want to display
        spacing (int): how many whitespaces and dash characters should be used when displaying a new line (has to be > 0)
        current_level (int): the current level of the tree (this shouldn't be given as a parameter on the first call)
    """
    
    if spacing <= 0:
        raise ValueError("spacing must be greater than 0")

    stack = [(term, current_level)]
    while stack:
        node, level = stack.pop()

        print(' ' * (spacing + 1) * (level - 1) + ('+' + '-' * spacing) * (level > 0) + node[0])

        if len(node) > 1:  # Check if there are children (more than one element)
            for child in node[1:]:
                stack.append((child, level + 1))
    

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
    
    print(list)
    
    return list
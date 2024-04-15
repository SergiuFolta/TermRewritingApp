from typing import Optional, List
from flask import flash
from .variables import *
from .functions import *
from .node import Node
from .representation_changes import ChangeListToTree, ChangeTreeToList
from .substitutions import *
from .database import *


def CountArguments(function_str: str) -> int:
    """
        This function counts the number of arguments a function has.
    Args:
        function_str (str): the remainder of the input string after the function character was found e.g
                            f(x, y) would mean function_str = "(x, y)"

    Returns:
        int: number of arguments this function has. returns -1 if it's an invalid string
    """
    function_str = function_str.replace(" ", "")
    arguments = 0 # assume this is a constant function
                    
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
        elif arguments == 0: # if this is not ",", "(" or ")" and arguments is 0, this means this is not a constant function as we assumed
            arguments = 1
        
    return arguments if open_brackets == 0 else -1


def LoadLanguage(input_str: str) -> None:
    """
        This function takes in a string argument and loads the 
        found functions and variables into their respective objects.
    Args:
        input_str (str): term to load the language from
    """
    functions = LoadFunctions()
    variables = LoadVariables()
    
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
                next_char_index = input_str.find("(", i + 1)
                if next_char_index == -1: # this is certainly a variable
                    variables.add(term)
                elif input_str[i + 1:next_char_index].count(" ") != (next_char_index - (i + 1)): 
                    # if there aren't just whitespaces, then the "(" is most likely from another function. Assume this is a variable
                    variables.add(term)
                    continue
                
                if input_str[next_char_index] == "(": # this has to be a function
                    functions[term] = CountArguments(input_str[next_char_index:])
                    
                    if functions[term] == -1:
                        flash(f"ERROR: String is invalid, couldn't determine number of arguments for function {term}!", category='error')
                        return
                else: # this is a variable
                    variables.add(term)
            elif term in functions:
                next_char_index = input_str.find("(", i + 1)
                if next_char_index == -1:
                    flash(f"ERROR: {term} found again, should be a function but is now a variable."
                            , category='error')
                    return
                elif functions[term] == 0 and input_str[i + 1:next_char_index].count(" ") != (next_char_index - (i + 1)): 
                    # if there aren't just whitespaces, then the "(" is most likely from another function. 
                    # Assume this is a constant function that was previously written with "()" notation
                    i += 1
                    continue
                    
                if input_str[next_char_index] == "(": # this has to be a function
                    arguments = CountArguments(input_str[next_char_index:])
                    
                    if arguments != functions[term]:
                        flash(f"ERROR: Function {term} found again, taking a different number of arguments than before! \
                                Found {functions[term]} before, now found {arguments}.", category='error')
                        return
                else: # this was previously recognized as a function, but is now a variable
                    flash(f"ERROR: {term} was previously a function, but is a variable in this term!", category="error")
                    return
            elif term in variables:
                next_char_index = input_str.find("(", i + 1)
                if input_str[i + 1:next_char_index].count(" ") == (next_char_index - (i + 1)):
                    # this means this is a function in our string, but was previously a variable
                    flash(f"ERROR: {term} found again, should be a variable but is now a function." , category='error')
                    return
        
        i += 1
    
    SaveFunctions(functions)
    SaveVariables(variables)


def CreateTree(input_str: str) -> Optional[Node] :
    """
        This function takes in a string argument and returns the corresponding 
        tree, if it can be created. It will otherwise return None.
    Args:
        input_str (str): term to create the tree from

    Returns:
        Optional[Node]: returns the head of the tree or None if it can't be created
    """
    
    functions = LoadFunctions()
    variables = LoadVariables()
    
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
            if current_node.next == None and current_node.value not in functions:
                flash("ERROR: There's an open paranthesis, but we're not expecting any arguments!", category='error')
                return None
            
            if functions[current_node.value] > 0:
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
            
            modified_str = input_str[:i + 1].replace(" ", "")
            if len(modified_str) - 1 - modified_str.rfind("(") != 1: # this would otherwise be a constant function and we don't want to jump
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
                print(current_node.value)
                flash("ERROR: Function given more arguments than it can accept!", category='error')
                return None
        elif str in variables:
            if current_node.value != "":
                flash("ERROR: More than one variable is trying to occupy the same node!", category='error')
                return None
            
            current_node.value = str

    return head


def PrintTree(head: Node, spacing: int = 2, current_level: int = 0) -> str:
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
    
    

def FlattenList(ls: List) -> List:
    """
    Helper function to flatten a nested list.

    Args:
        list (List): Nested list to flatten

    Returns:
        List: Flattened list
    """
    flatList = []
    # Iterate with outer list
    for element in ls:
        if type(element) == list:
            flatList += FlattenList(element)
        else:
            flatList.append(element)
    
    return flatList


def GetPositionFromListIndex(term: List, index: int) -> str:
    """
    This function takes in an index from the term (imagine it as one long non-nested list)
    and returns the position of the element taking into consideration our nested list encoding.

    Args:
        term (List): list representing a term
        index (int): the index of the subterm we'd like to get 

    Returns:
        str: position of the subterm you'd like to get (in format "{number}_{number}_{number}").
                If you want to get the root, position is = ""
    """
    position = ""
    
    if index == 0:
        return position
    
    term = term[1:]
    if len(term) == 1:
        term = term[0]
    
    while index != 0:
        curr_position = 0
        for item in term:
            if type(item) == list:
                flatList = FlattenList(item)
                
                if len(flatList) < index:
                    index -= len(flatList)
                else:
                    position += f"_{str(curr_position)}"
                    term = item
                    break
            else:
                curr_position += 1
                index -= 1
                
                if index == 0:
                    position += f"_{str(curr_position)}"
                    break
    
    return position[1:] # Skip the first character, which will always be _


def GetSubtermAtPosition(term: List, position: str = "") -> List:
    """
    This function takes in a position from the term and returns the subterm from
    that position onward.

    Args:
        term (List): list representing a term
        position (str): position of the subterm you'd like to get (in format "{number}_{number}_{number}").
                        If you want to get the root, position is = ""

    Returns:
        List: returns the list of lists or [] if there's an error
    """
    if position == "":
        return term
    
    indeces = position.split("_")
    
    for index in indeces:
        term = term[1]
        index = int(index) - 1

        if index + 1 >= len(term):
            flash("ERROR: There are not enough subterms for index {index}!", category="error")
            return
        
        term = term[index : index + 2]
        
    return term


def ReplaceSubtermAtPosition(original_term: List, replacement_term: List, position: str = "") -> List:
    """
    This function takes in a position from {original_term} and returns a new term created from replacing
    everything from {position} in {original_term} with {replacement_term}.
    This function does NOT modify {original_term} outside of its scope.
    
    Args:
        original_term (List): list representing a term which will be built on top of
        replacement_term (List): list representing a term which will replace a subterm from {original_term}
        position (str): position of the subterm you'd like to get (in format "{number}_{number}_{number}").
                        If you want to get the root, position is = ""

    Returns:
        List: returns the new term after replacement
    """
    if position == "":
        return replacement_term
    
    indeces = position.split("_")
    
    head = ChangeListToTree(original_term)
    
    curr_node = head
    for i in range(0, len(indeces) - 1):
        index = int(indeces[i]) - 1
        if curr_node.next != None:
            curr_node = curr_node.next[index]
        else:
            flash(f"ERROR: Cannot replace subterm at index {index + 1}! The position {position} doesn't exist.", category="error")
            return []
    
    curr_node.next[(int(indeces[-1]) - 1)] = ChangeListToTree(replacement_term)
    
    new_term = ChangeTreeToList(head)
    
    return new_term


def IsTermGround(term: List) -> bool:
    """
    This function takes in a term and checks if it is ground (there are no variables).
    
    Args:
        term (List): list representing a term

    Returns:
        bool: returns True if term is ground
    """
    variables = LoadVariables()
    
    if len(variables) == 0:
        return True # there are no variables in our language, so of course this is ground
    
    stack = [term]
    while stack:
        curr_term = stack.pop()
        value = curr_term[0]
        
        if value in variables:
            return False # found a variable, quit.
        
        if len(curr_term) > 1:
            stack.append(curr_term[1]) # append the next children for checking in the stack
        
        for i in range(2, len(curr_term), 2):
            if i + 1 != len(curr_term):
                if type(curr_term[i + 1]) == list:
                    stack.append([curr_term[i], curr_term[i + 1]]) # append the siblings and their children for checking in the stack
            else:
                stack.append([curr_term[i]])
    
    return True # passed all checks, this is ground

from typing import Optional, List, Tuple
from flask import flash
from .node import Node
from .database import LoadFunctions, LoadVariables


def CreateTree(input_str: str) -> Optional[Node]:
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
    
    input_str = input_str.replace(" ", "") # don't allow any whitespaces, they only make things more difficult
    i = 0
    while i < len(input_str):
        str = input_str[i]
        
        if str not in "(),":
            # this case looks out for variable names of varying length
            while i + 1 < len(input_str) and input_str[i + 1] not in "(),":
                i += 1
                str += input_str[i]
        
        if str in functions.keys(): # if current string represents a function
            if current_node.value != "":
                flash("ERROR: More than one function is trying to occupy the same node!", category='error')
                return None
            current_node.value = str # first we note this down as our current value
            
            if functions[str] > 0: # if the number of arguments is higher than 0
                current_node.next = [] # we prepare a list of Nodes

                for _ in range(0, functions[str]): # then we add as many further Nodes as the function has possible arguments
                    current_node.next.append(Node(previous=current_node))
        elif str == '(':
            if current_node.value in variables:
                flash("ERROR: There's an open paranthesis, but we're not expecting any arguments!", category='error')
                return None
            
            if functions[current_node.value] > 0:
                current_node = current_node.next[0] # we go in the first Node in the list of children of the current one
            elif input_str[i + 1] == ')':
                i += 1 # constant function with paranthesis, but it's well closed so we just move on.
            else:
                flash("ERROR: There's an open paranthesis, but the current function is constant!", category='error')
                return None
        elif str == ')':
            if current_node.previous == None: # we have no parent to jump to in our tree
                flash("ERROR: There are too many closed parantheses!", category='error')
                return None
            
            if current_node.next != None: # if this is a function
                for node in current_node.next: # we check all children
                    if node.value == "": # and make sure none are still expecting a value
                        flash("ERROR: Function is still expecting arguments!", category='error')
                        return None
            
            # not sure why this case is here so let's just comment it out for now
            # if current_node.value == "":
            #     flash("ERROR: Function is still expecting arguments!", category='error')
            #     return None
            
            current_node = current_node.previous # we jump one level above our current one
        elif str == ',':
            if current_node.previous == None: # if there is no higher level to jump to
                flash("ERROR: Too many commas!", category='error')
                return None
            
            current_child = current_node
            current_node = current_node.previous # we need to jump a level up

            child_index = current_node.next.index(current_child)
            
            if child_index + 1 == len(current_node.next): # this is the last argument we were expecting
                flash("ERROR: There are more arguments for this function than we were expecting! Check commas.", category="error")
                return None
            
            current_node = current_node.next[child_index + 1]
        elif str in variables:
            if current_node.value != "":
                flash("ERROR: More than one variable is trying to occupy the same node!", category='error')
                return None
            
            current_node.value = str
        
        i += 1

    return head


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
    
    if head.next:
        list.append(AppendChildrenNodesToList(head))
    
    return list


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
    if len(term) > 1:
        AppendChildrenToNode(term[1], head)
    
    return head


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
    
    children_stack = []
    
    for subterm in term:
        if type(subterm) == list:
            children_stack.append(subterm)
            current_node.next[-1].next = []
        else:
            if current_node.next == None:
                current_node.next = []
            
            current_node.next.append(Node(value = subterm, previous = current_node))
    
    if current_node.next != None:
        for child in current_node.next:
            if child.next == []:
                AppendChildrenToNode(children_stack.pop(0), child)
                
                
def CreateInputStringFromTree(head: Node) -> str:
    string = f"{head.value}"
    if head.next != None:
        string += "("
    
    if head.previous != None:
        if head != head.previous.next[0]:
            string = ", " + string
        
    if head.next != None:
        for child in head.next:
            string += CreateInputStringFromTree(child)
            
    if head.previous != None:
        if head == head.previous.next[-1]:
            string += ")"
    
    return string


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


def ModifyListToArgumentList(ls: List) -> List:
    argumentList = []
    
    ls = ChangeTreeToList(ChangeListToTree(ls))
    
    ls = FlattenList(ls)
    
    functions = LoadFunctions()
    
    for term in ls:
        if term in functions.keys():
            argumentList.append(functions[term])
        else:
            argumentList.append(0)
    
    return argumentList

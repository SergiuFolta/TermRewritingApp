from typing import Optional, List, Tuple
from flask import flash
from .node import Node

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
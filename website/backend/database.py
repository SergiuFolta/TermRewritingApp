from flask import session, flash
from typing import List, Optional, Tuple

def SaveVariables(variables: set) -> None:
    """
    This function saves the {variables} set in the current user session.

    Args:
        variables (set): set which includes the variables in our language
    """
    session["variables"] = list(variables) # sets aren't JSON serializable
    

def LoadVariables() -> set:
    """
    This function loads the {variables} set from the current user session, 
    or creates a new set if it doesn't exist.

    Returns:
        set: the set containing the variables in our language
    """
    return set(session["variables"]) if "variables" in session else set([]) # sets aren't JSON serializable


def SaveFunctions(functions: dict) -> None:
    """
    This function saves the {functions} dictionary in the current user session.

    Args:
        functions (dict): dictionary which includes the functions in our language and their arity
    """
    session["functions"] = functions
    

def LoadFunctions() -> dict:
    """
    This function loads the {functions} dictionary from the current user session, 
    or creates a new dictionary if it doesn't exist.

    Returns:
        dict: the dictionary containing the functions in our language and their arity
    """
    return session["functions"] if "functions" in session else {}


def SaveSubstitutions(substitutions: dict) -> None:
    """
    This function saves the {substitutions} dictionary in the current user session.

    Args:
        substitutions (dict): dictionary which includes the substitutions
    """
    session["substitutions"] = substitutions
    

def LoadSubstitutions() -> dict:
    """
    This function loads the {substitutions} dictionary from the current user session, 
    or creates a new dictionary if it doesn't exist.

    Returns:
        dict: the dictionary containing the substitutions
    """
    return session["substitutions"] if "substitutions" in session else {}


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

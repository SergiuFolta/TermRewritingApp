from flask import session, flash
from typing import List, Optional, Tuple, Dict

def SaveVariables(variables: set) -> None:
    """
    This function saves the {variables} set in the current user session.

    Args:
        variables (set): set which includes the variables in our language
    """
    session["variables"] = list(variables)
    

def LoadVariables() -> set:
    """
    This function loads the {variables} set from the current user session, 
    or creates a new set if it doesn't exist.

    Returns:
        set: the set containing the variables in our language
    """
    return set(session["variables"]) if "variables" in session else set([])


def SaveFunctions(functions: dict) -> None:
    """
    This function saves the {functions} dictionary in the current user session.

    Args:
        functions (dict): dictionary which includes the functions in our language and their arity
    """
    session["functions"] = functions
    
    ModifyPrecedence()
    

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
    print(term_dictionary)
    session["terms"] = term_dictionary


def LoadTerm(name: str) -> Optional[Tuple[str, List]]:
    """
    This function takes in the name of a term and returns the contents within a list of lists.

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


def LoadTermByList(term : List) -> Optional[Tuple[str, List]]:
    """
    This function takes in the name of a term and returns the contents within a list of lists.

    Args:
        name (str): the name by which to remember this term

    Returns:
        Optional[Tuple[str, List]]: returns a tuple with the string representation 
        and the list of lists or None if there's an error
    """
    term_dictionary = session["terms"] if "terms" in session else {}
    
    flat_term = FlattenList(term)
    
    for key, value in term_dictionary.items():
        if flat_term == FlattenList(value[1]):
            return term_dictionary[key]
    
    flash(f"ERROR: No term with the list {term} found in the dictionary!", category="error")
    return None
    

def LoadAllTerms() -> Optional[Dict[str, Tuple[str, List]]]:
    """
    This function returns all terms currently in the session.

    Returns:
        Optional[Dict[str, Tuple[str, List]]]: returns a dictionary of tuples with the string representation 
        and the list of lists or None if there's an error
    """
    return (session["terms"] if "terms" in session else {})


def DeleteTerms() -> None:
    """
    This function deletes all terms currently found in the session.
    """
    session.pop("terms")
    flash("WARNING: All terms have been deleted because a function or variable contained in an existing term has been modified!")


def SavePrecedences(precedences: dict) -> None:
    """
    This function saves the {precedences} dictionary in the current user session.

    Args:
        precedences (dict): dictionary which includes the precedences in our language
    """
    session["precedences"] = precedences
    

def LoadPrecedences() -> Dict[str, int]:
    """
    This function returns the dictionary with the precedences in our language.

    Returns:
        Dict[str, int]: returns a dictionary with the name of the atomic term and their precedence
    """
    return session["precedences"] if "precedences" in session else {}


def ModifyPrecedence() -> None:
    functions = LoadFunctions()
    functions = dict(sorted(functions.items(), key=lambda item: item[1]))
    current_precedence = 0

    precedences = {}
    
    for func in functions.keys():
        precedences[func] = current_precedence
        current_precedence += 1

    SavePrecedences(precedences)


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

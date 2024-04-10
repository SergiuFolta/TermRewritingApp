from flask import session, flash
from .variables import LoadVariables

def ModifyFunction(old_function_name: str, curr_function_name: str, function_arity: int) -> None:
    """
    This function modifies an entry in the function dictionary.

    Args:
        old_function_name (str): old name of the function (can be the same as curr_function_name)
        curr_function_name (str): current name of the function (can be the same as old_function_name)
        function_arity (int): arity of the function (value of the key in the dictionary)
    """
    if "functions" not in session:
        flash("ERROR: There are no functions loaded in the session.", category="error")
        return
    
    functions = LoadFunctions()
    variables = LoadVariables()
    
    if old_function_name not in functions:
        flash(f"ERROR: Could not find function {old_function_name} in dictionary!", category="error")
        return

    if old_function_name != curr_function_name: # modify the function key name if requsted
        if curr_function_name in variables:
            flash(f"ERROR: Function {curr_function_name} is a variable!", category="error")
            return
        
        functions[curr_function_name] = functions.pop(old_function_name)
    
    functions[curr_function_name] = function_arity # modify the function arity
    
    SaveFunctions(functions)

    flash(f"Successfully modified function {old_function_name} into function {curr_function_name} with arity {function_arity}!")


def AddFunction(function_name: str, function_arity: int, verbose: bool = True) -> None:
    """
    This function adds an entry in the function dictionary.

    Args:
        function_name (str): name of the function to add (the key in the dictionary)
        function_arity (int): arity of the function (value of the key in the dictionary)
        verbose (bool): if True, will flash messages to website
    """
    functions = LoadFunctions()

    if function_name in functions:
        flash(f"ERROR: There is already a function with the name {function_name} in our dictionary!", category="error")
        return
    
    variables = LoadVariables()
    
    if function_name in variables:
        flash(f"ERROR: There is already a variable with the name {function_name}!", category="error")
        return

    functions[function_name] = function_arity
    
    SaveFunctions(functions)
    
    if verbose:
        flash(f"Successfully added function {function_name} with arity {function_arity}!")
    
    
def DeleteFunction(function_name: str, verbose: bool = True) -> None:
    """
    This function deletes an entry in the function dictionary.

    Args:
        function_name (str): name of the function to delete (the key in the dictionary)
        verbose (bool): if True, will flash messages to website
    """
    functions = LoadFunctions()

    if function_name not in functions:
        flash(f"ERROR: There is no function with the name {function_name} in our dictionary!", category="error")
        return

    functions.pop(function_name)
    
    SaveFunctions(functions)
    if verbose:
        flash(f"Successfully deleted function {function_name}!")
    

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

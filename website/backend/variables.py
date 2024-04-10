from flask import session, flash
from .functions import LoadFunctions

def ModifyVariable(old_variable_name: str, curr_variable_name: str) -> None:
    """
    This function modifies an entry in the variables set.

    Args:
        old_variable_name (str): old name of the function (can be the same as curr_variable_name)
        curr_variable_name (str): current name of the function (can be the same as old_variable_name)
    """
    if "variables" not in session:
        flash("ERROR: There are no variables loaded in the session.", category="error")
        return
    
    variables = LoadVariables()
    
    if old_variable_name not in variables:
        flash(f"ERROR: Could not find variable {old_variable_name} in our set!", category="error")
        return

    if old_variable_name != curr_variable_name: # modify the variable name if requsted
        functions = LoadFunctions()
        if curr_variable_name in functions:
            flash(f"ERROR: There is already a function with the name {curr_variable_name}!", category="error")
            return
        
        DeleteVariable(old_variable_name, False)
        AddVariable(curr_variable_name, False)
    
        SaveVariables(variables)

        flash(f"Successfully modified variable {old_variable_name} into variable {curr_variable_name}!")


def AddVariable(variable_name: str, verbose: bool = True) -> None:
    """
    This function adds an entry in the variable set.

    Args:
        variable_name (str): name of the variable to add
        verbose (bool): if True, will flash messages to website
    """
    variables = LoadVariables()

    if variable_name in variables:
        flash(f"ERROR: There is already a variable with the name {variable_name}!", category="error")
        return

    functions = LoadFunctions()
    if variable_name in functions:
        flash(f"ERROR: There is already a function with the name {variable_name}!", category="error")
        return

    variables.add(variable_name)
    
    SaveVariables(variables)

    if verbose:
        flash(f"Successfully added variable {variable_name}!")
    
    
def DeleteVariable(variable_name: str, verbose: bool = True) -> None:
    """
    This function deletes an entry in the variables set.

    Args:
        variable_name (str): name of the variable to delete
        verbose (bool): if True, will flash messages to website
    """
    variables = LoadVariables()

    if variable_name not in variables:
        flash(f"ERROR: There is no variable with the name {variable_name}!", category="error")
        return

    variables.remove(variable_name)
    
    SaveVariables(variables)
    
    if verbose:
        flash(f"Successfully deleted function {variable_name}!")
    

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
from flask import session, flash

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
    
    variables = set(session["variables"])
    
    if old_variable_name not in variables:
        flash(f"ERROR: Could not find variable {old_variable_name} in our set!", category="error")
        return

    if old_variable_name != curr_variable_name: # modify the variable name if requsted
        functions = session["functions"] if "functions" in session else {}
        if curr_variable_name in functions:
            flash(f"ERROR: There is already a function with the name {curr_variable_name}!", category="error")
            return
        
        variables.remove(old_variable_name)
        variables.add(curr_variable_name)
    
        session["variables"] = list(variables)

        flash(f"Successfully modified variable {old_variable_name} into variable {curr_variable_name}!")


def AddVariable(variable_name: str) -> None:
    """
    This function adds an entry in the variable set.

    Args:
        variable_name (str): name of the variable to add
    """
    variables = set(session["variables"]) if "variables" in session else set([])

    if variable_name in variables:
        flash(f"ERROR: There is already a variable with the name {variable_name}!", category="error")
        return

    functions = session["functions"] if "functions" in session else {}
    if variable_name in functions:
        flash(f"ERROR: There is already a function with the name {variable_name}!", category="error")
        return

    variables.add(variable_name)
    
    session["variables"] = list(variables)

    flash(f"Successfully added variable {variable_name}!")
    
    
def DeleteVariable(variable_name: str) -> None:
    """
    This function deletes an entry in the variables set.

    Args:
        variable_name (str): name of the variable to delete
    """
    variables = set(session["variables"]) if "variables" in session else {}

    if variable_name not in variables:
        flash(f"ERROR: There is no variable with the name {variable_name}!", category="error")
        return

    variables.remove(variable_name)
    
    session["variables"] = list(variables)
    
    flash(f"Successfully deleted function {variable_name}!")
    
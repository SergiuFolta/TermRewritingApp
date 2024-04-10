from flask import session, flash
from typing import List
from .database import *

def ModifySubstitution(old_substitution_input: str, old_substitution_output: str, 
                        new_substitution_input: str, new_substitution_output: str) -> None:
    """
    This function modifies an entry in the substitution dictionary.

    Args:
        old_substitution_input (str): the old left-hand side member of the substitution
        old_substitution_output (str): the old right-hand side member of the substitution
        new_substitution_input (str): the new left-hand side member of the substitution
        new_substitution_output (str): the new right-hand side member of the substitution
    """
    old_substitution_input.replace(" ", "")
    new_substitution_input.replace(" ", "")
    old_substitution_output.replace(" ", "")
    new_substitution_output.replace(" ", "")
    
    if "substitutions" not in session:
        flash("ERROR: There are no substitutions loaded in the session.", category="error")
        return
    
    substitutions = LoadSubstitutions()
    
    if old_substitution_input not in substitutions.keys():
        flash(f"ERROR: Could not find {old_substitution_input} as an input for any substitution!", category="error")
        return
    
    if old_substitution_output not in substitutions[old_substitution_input]:
        flash(f"ERROR: Could not find any substitution going from {old_substitution_input} to {old_substitution_output}!", category="error")
        return

    if old_substitution_input != new_substitution_input: # modify the substitution input if requsted
        DeleteSubstitution(old_substitution_input, old_substitution_output, False)
        AddSubstitution(new_substitution_input, new_substitution_output, False)
    else:
        DeleteSubstitution(old_substitution_input, old_substitution_output, False)
        AddSubstitution(old_substitution_input, new_substitution_output, False)

    flash(f"Successfully modified substitution {old_substitution_input} to {old_substitution_output} \
            into {new_substitution_input} to {new_substitution_output}!")


def AddSubstitution(substitution_input: str, substitution_output: str, verbose: bool = True) -> None:
    """
    This function adds an entry in the substitution dictionary.
    If {substitution_input} exists in the dictionary, then add another
    output to its list.
    Otherwise, create a new list for its value.

    Args:
        substitution_input (str): the left-hand side member of the substitution
        substitution_output (str): the right-hand side member of the substitution
        verbose (bool): if True, will flash messages to website
    """
    substitution_input.replace(" ", "")
    substitution_output.replace(" ", "")
    
    substitutions = LoadSubstitutions()

    if substitution_input in substitutions.keys():
        if substitution_output in substitutions[substitution_input]:
            flash(f"ERROR: There is already a substitution going from {substitution_input} to {substitution_output}.",
                    category="error")
            return
        
        substitutions[substitution_input].append(substitution_output)
    else:
        substitutions[substitution_input] = [substitution_output]

    SaveSubstitutions(substitutions)

    if verbose:
        flash(f"Successfully added a substitution from {substitution_input} to {substitution_output}!")
    
    
def DeleteSubstitution(substitution_input: str, substitution_output: str, verbose: bool = True) -> None:
    """
    This function deletes a subtitution in the substitutions dictionary.

    Args:
        substitution_input (str): the left-hand side member of the substitution
        substitution_output (str): the right-hand side member of the substitution
        verbose (bool): if True, will flash messages to website
    """
    substitution_input.replace(" ", "")
    substitution_output.replace(" ", "")
    
    substitutions = LoadSubstitutions()

    if substitution_input not in substitutions.keys():
        flash(f"ERROR: There is no subtitution with the input {substitution_input}!", category="error")
        return
    
    if substitution_output not in substitutions[substitution_input]:
        flash(f"ERROR: There is no subtitution going from {substitution_input} to {substitution_output}!", category="error")
        return

    if len(substitutions[substitution_input]) == 1:
        substitutions.pop(substitution_input)
    else:
        substitutions[substitution_input].remove(substitution_output)
    
    SaveSubstitutions(substitutions)
    
    if verbose:
        flash(f"Successfully deleted the substitution going from {substitution_input} to {substitution_output}!")


def RuleDeleteSubstitutions(substitutions: dict, verbose: bool = False) -> dict:
    """
    Unification problem - Delete rule implementation. This function will delete
    all substitutions of the form {x -> x}.

    Args:
        substitutions (dict): the dictionary of substitutions

    Returns:
        dict: {substituions} after removing all entries satisfying the rule above
    """
    modified_substitutions = substitutions
    for input in substitutions.keys():
        for output in substitutions[input]:
            if input == output:
                if len(modified_substitutions[input]) == 1:
                    modified_substitutions.pop(input)
                else:
                    modified_substitutions[input].remove(output)
                    
                if verbose:
                    flash(f"Successfully removed substitution {input} to {output}!")
    
    return modified_substitutions

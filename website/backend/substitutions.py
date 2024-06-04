from flask import session, flash
from typing import List
from .database import *
from .representation_changes import ChangeTreeToList, CreateTree, CreateInputStringFromTree, ChangeListToTree

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
    old_substitution_input = old_substitution_input.replace(" ", "")
    new_substitution_input = new_substitution_input.replace(" ", "")
    old_substitution_output = old_substitution_output.replace(" ", "")
    new_substitution_output = new_substitution_output.replace(" ", "")
    
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
    substitution_input = substitution_input.replace(" ", "")
    substitution_output = substitution_output.replace(" ", "")
    
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
    substitution_input = substitution_input.replace(" ", "")
    substitution_output = substitution_output.replace(" ", "")
    
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
        dict: {substitutions} after removing all entries satisfying the rule above
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


def RuleDecomposeSubstitutions(substitutions: dict, verbose: bool = False) -> dict:
    """
    Unification problem - Decompose rule implementation. This function will decompose
    all substitutions of the form {f(x1...xn) -> f(t1...tn)} into {x1 -> t1 ... xn -> tn}.

    Args:
        substitutions (dict): the dictionary of substitutions

    Returns:
        dict: {substitutions} after decomposing all entries satisfying the rule above
    """
    modified_substitutions = substitutions
    
    for input in substitutions.keys():
        firstTerm = input.find("(")
        if firstTerm == -1:
            continue
        firstTerm = input[:firstTerm]
        
        for output in substitutions[input]:
            secondTerm = input.find("(")
            if secondTerm == -1:
                continue
            secondTerm = output[:secondTerm]
            
            if firstTerm == secondTerm:
                term1 = ChangeTreeToList(CreateTree(input))
                term2 = ChangeTreeToList(CreateTree(output))
                
                for arg1, arg2 in zip(term1[1], term2[1]):
                    str1 = CreateInputStringFromTree(ChangeListToTree(arg1))
                    str2 = CreateInputStringFromTree(ChangeListToTree(arg2))
                    
                    if str1 in modified_substitutions.keys():
                        modified_substitutions[str1].append(str2)
                    else:
                        modified_substitutions[str1] = [str2]
                
                if len(modified_substitutions[input]) == 1:
                    modified_substitutions.pop(input)
                else:
                    modified_substitutions[input].remove(output)
                
            if verbose:
                flash(f"Successfully decomposed substitution {input} to {output}!")
    
    return modified_substitutions


def RuleOrientSubstitutions(substitutions: dict, verbose: bool = False) -> dict:
    """
    Unification problem - Orient rule implementation. This function will orient
    all substitutions of the form {t -> x} to {x -> t}, if t is not a variable

    Args:
        substitutions (dict): the dictionary of substitutions

    Returns:
        dict: {substitutions} after orienting all entries satisfying the rule above
    """
    modified_substitutions = substitutions
    
    for input in substitutions.keys():        
        for output in substitutions[input]:
            term = ChangeListToTree(CreateTree(output))
            
            if IsTermGround(term):
                if output in modified_substitutions.keys():
                    modified_substitutions[output].add(input)
                else:
                    modified_substitutions[output] = [input]
                
                if len(modified_substitutions[input]) == 1:
                    modified_substitutions.pop(input)
                else:
                    modified_substitutions[input].remove(output)
                
            if verbose:
                flash(f"Successfully oriented substitution {input} to {output}!")
    
    return modified_substitutions


def RuleEliminateSubstitutions(substitutions: dict, verbose: bool = False) -> dict:
    """
    Unification problem - Eliminate rule implementation. This function will eliminate
    all known variables from the right-hand side of any substitution that does not contain it.

    Args:
        substitutions (dict): the dictionary of substitutions

    Returns:
        dict: {substitutions} after eliminating all entries satisfying the rule above
    """
    modified_substitutions = substitutions
    
    for input in substitutions.keys():        
        term = ChangeListToTree(CreateTree(input))
        if len(term) == 1: # this is a variable
            termToReplace = ""
            for output in substitutions[input]:
                termOutput = ChangeListToTree(CreateTree(output))
                if term[0] in FlattenList(termOutput):
                    continue
                
                termToReplace = output
                
                for input2 in substitutions.keys():
                    
                    for output2 in substitutions.keys():
                        
                        if verbose:
                            flash(f"Successfully eliminated substitution {input2} to {output2}!")
    
    return modified_substitutions


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
        
        if value in variables.keys():
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

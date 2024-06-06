from flask import session, flash
from typing import List
from .database import *
from .representation_changes import ChangeTreeToList, CreateTree, CreateInputStringFromTree, ChangeListToTree, ModifyListToArgumentList

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
    modified_substitutions = {}
    for key, value in substitutions.items():
        modified_substitutions[key] = []
        for entry in value:
            modified_substitutions[key].append(entry)
    
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
    modified_substitutions = {}
    for key, value in substitutions.items():
        modified_substitutions[key] = []
        for entry in value:
            modified_substitutions[key].append(entry)
    
    for input in substitutions.keys():
        firstTerm = input.find("(") # this is a function if this is found
        if firstTerm == -1: # in this case we don't find it
            continue
        firstTerm = input[:firstTerm] # get the function value
        
        for output in substitutions[input]:
            secondTerm = input.find("(") # this is a function if this is found
            if secondTerm == -1: # in this case we don't find it
                continue
            secondTerm = output[:secondTerm] # get the function value
            
            if firstTerm == secondTerm: # if the function symbol is the same
                term1 = ChangeTreeToList(CreateTree(input))
                term2 = ChangeTreeToList(CreateTree(output))
                
                for arg1, arg2 in zip(term1[1], term2[1]):
                    str1 = CreateInputStringFromTree(ChangeListToTree(arg1))
                    str2 = CreateInputStringFromTree(ChangeListToTree(arg2))
                    
                    if str1 in modified_substitutions.keys():
                        if str2 not in modified_substitutions[str1]:
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
    modified_substitutions = {}
    for key, value in substitutions.items():
        modified_substitutions[key] = []
        for entry in value:
            modified_substitutions[key].append(entry)
    
    for input in substitutions.keys():
        if TermIsVariable(ChangeTreeToList(CreateTree(input))):
            continue
        
        for output in substitutions[input]:
            term = ChangeTreeToList(CreateTree(output))
            
            if TermIsVariable(term):
                if output in modified_substitutions.keys():
                    if input not in modified_substitutions[output]:
                        modified_substitutions[output].append(input)
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
    modified_substitutions = {}
    for key, value in substitutions.items():
        modified_substitutions[key] = []
        for entry in value:
            modified_substitutions[key].append(entry)
            
    # for input in substitutions.keys():        
    #     term = ChangeTreeToList(CreateTree(input))
    #     if len(term) == 1: # this is a variable
    #         for output in substitutions[input]:
    #             termOutput = ChangeTreeToList(CreateTree(output))
    #             if term[0] in FlattenList(termOutput): # verify that the left hand side variable is not in the right hand side
    #                 continue
                
    #             for input2 in substitutions.keys():
    #                 if input2 not in modified_substitutions.keys():
    #                     continue
                    
    #                 termToModify = ChangeTreeToList(CreateTree(input2))
    #                 valueInput = ApplySubstitution((input, output), termToModify)
    #                 actualInput = input2
                    
    #                 if valueInput != None:
    #                     print(f"For {input2}, the current substitutions are: {modified_substitutions}")
    #                     newInput = CreateInputStringFromTree(ChangeListToTree(valueInput))
    #                     print(newInput)
    #                     modified_substitutions[newInput] = []
                        
    #                     for subst in substitutions[input2]:
    #                         if subst == output or subst == input:
    #                             continue
                            
    #                         if subst not in modified_substitutions[newInput]:
    #                             print(subst)
    #                             modified_substitutions[newInput].append(subst)
    #                             modified_substitutions[input2].remove(subst)
                            
    #                     if len(modified_substitutions[newInput]) == len(substitutions[input2]) and newInput != input2:
    #                         modified_substitutions.pop(input2)
                            
    #                         actualInput = newInput
    #                     elif len(modified_substitutions[newInput]) == 0:
    #                         modified_substitutions.pop(newInput)
                        
    #                     continue
                    
    #                 for output2 in substitutions[input2]:
    #                     if input2 == output2:
    #                         continue
                        
    #                     termToModify = ChangeTreeToList(CreateTree(output2))
    #                     value = ApplySubstitution((input, output), termToModify)
    #                     if value != None:
    #                         newInput = CreateInputStringFromTree(ChangeListToTree(value))
    #                         modified_substitutions[actualInput].append(CreateInputStringFromTree(ChangeListToTree(value)))
                        
    #                     if verbose:
    #                         flash(f"Successfully eliminated substitution {input2} to {output2}!")
    
    i = 0
    while i < len(modified_substitutions.keys()):
        input = list(modified_substitutions.keys())[i]
        i += 1
        term = ChangeTreeToList(CreateTree(input))
        
        if TermIsVariable(term): # input needs to be a variable in some output
            j = 0
            while j < len(modified_substitutions[input]):
                output = modified_substitutions[input][j]
                j += 1
                if term[0] not in FlattenList(ChangeTreeToList(CreateTree(output))): # input is a variable and not in the rhs
                    substitutionToApply = (input, output)
                    
                    left_rules = [] # this is where we store the rules which we might modify (in which the input is in the lhs)
                    right_rules = [] # this is where we store the rules which we might modify (in which the input is in the rhs ONLY)
                    for checkInput in modified_substitutions.keys():
                        if term[0] in FlattenList(ChangeTreeToList(CreateTree(checkInput))): # if input is in the lhs of the rule
                            for checkOutput in modified_substitutions[checkInput]:
                                if checkOutput == checkInput: # rhs and lhs are the same
                                    continue
                                
                                if checkOutput == substitutionToApply[1] and checkInput == substitutionToApply[0]: # rule is the same as the substitution we're trying to apply
                                    continue
                                
                                left_rules.append((checkInput, checkOutput))
                        else:
                            for checkOutput in modified_substitutions[checkInput]:
                                if term[0] in FlattenList(ChangeTreeToList(CreateTree(checkOutput))):
                                    right_rules.append((checkInput, checkOutput))
                    
                    # print(f"----------------------------------------------------------------------")
                    # print(f"For substitution: {substitutionToApply}")
                    # print(f"Before substitutions: {modified_substitutions}")
                    # print(f"Left rules: {left_rules}")
                    for rule in left_rules:
                        newTerm = ApplySubstitutionRecursive(substitutionToApply, ChangeTreeToList(CreateTree(rule[0])))
                        newInput = CreateInputStringFromTree(ChangeListToTree(newTerm))
                        
                        if newInput not in modified_substitutions.keys():
                            modified_substitutions[newInput] = []
                        
                        modified_substitutions[newInput].append(rule[1])
                        
                        if len(modified_substitutions[rule[0]]) == 1:
                            modified_substitutions.pop(rule[0])
                        else:
                            modified_substitutions[rule[0]].remove(rule[1])

                        newTerm = ApplySubstitutionRecursive(substitutionToApply, ChangeTreeToList(CreateTree(rule[1])))
                        if newTerm != None:
                            newOutput = CreateInputStringFromTree(ChangeListToTree(newTerm))
                            
                            modified_substitutions[newInput].remove(rule[1])
                            modified_substitutions[newInput].append(newOutput)
                        
                    # print(f"Right rules: {right_rules}")
                    for rule in right_rules:
                        newTerm = ApplySubstitutionRecursive(substitutionToApply, ChangeTreeToList(CreateTree(rule[1])))
                        newInput = CreateInputStringFromTree(ChangeListToTree(newTerm))
        
                        modified_substitutions[rule[0]].remove(rule[1])
                        modified_substitutions[rule[0]].append(newInput)
                    
                    # print(f"After substitutions: {modified_substitutions}")
    
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


def ApplySubstitutionRecursive(substitution : Tuple[str, str], term : List) -> Optional[List]:
    substitutionInput = ChangeTreeToList(CreateTree(substitution[0]))

    newTerm = ChangeTreeToList(ChangeListToTree(term))

    if substitutionInput == newTerm:
        newTerm = ChangeTreeToList(CreateTree(substitution[1]))
    else:
        subterms = []
        i = 0
        if len(newTerm) == 1: # constant function
            return None
        
        term_args = newTerm[1]
        while i < len(term_args):
            if i + 1 == len(term_args): # last element
                subterms.append([term_args[i]])
                i += 1
            elif type(term_args[i + 1]) == list: # this is a function
                subterms.append([term_args[i], term_args[i + 1]])
                i += 2
            else: # this is a variable
                subterms.append([term_args[i]])
                i += 1
        
        changed = False
        for index, subterm in enumerate(subterms):
            newerTerm = ApplySubstitutionRecursive(substitution, subterm)
            if newerTerm != None:
                subterms[index] = newerTerm
                changed = True
        
        if not changed:
            return None
        
        newTerm[1] = []
        for subterm in subterms:
            for subsubterm in subterm:
                newTerm[1].append(subsubterm)
        
    return newTerm


def ApplySubstitution(substitution : Tuple[str, str], term : List) -> Optional[List]:
    # f(f(x, y), z) -> f(x, f(y, z))
    # f(f(x, y), i(f(x, y))) -> f(x, f(y, i(f(x, y))))
    
    # f(f(x, y), z) -> ["f", ["f", ["x", "y"], "z"]] ->                             [2, [0, 2, [0, 0]]]
    # f(f(x, y), i(f(x, y))) -> ["f", ["f", ["x", "y"], "i", ["f", ["x", "y"]]]] ->  [2, [1, [2, [0, 0]], 2, [0, 0]]]

    # [2, 2, 0, 0, 0]
    # [2, 2, 0, 0, 1, 2, 0, 0]
    # argumentCount = 2
    # ()
    # [2, 0, 0, 0]
    # [2, 0, 0, 1, 2, 0, 0]
    # argumentCount = 1
    # ()
    # [0]
    # [1, 2, 0, 0]
    # argumentCount = 1
    # (x -> x, y -> y)
    # []
    # []
    # argumentCount = 0
    # (x -> x, y -> y, z -> i(f(x, y)))
    
    # [2, 0, 1, 0] f(x', i(x'))
    # [2, 2, 0, 0, 1, 2, 0, 0] f(f(x, y), i(f(x, y)))
    # argumentCount = 2
    # ()
    # [0, 1, 0]
    # [2, 0, 0, 1, 2, 0, 0]
    # argumentCount = 2
    # ()
    # [1, 0]
    # [1, 2, 0, 0]
    # argumentCount = 1
    # (x' -> f(x, y))
    # [0]
    # [2, 0, 0]
    # argumentCount = 1
    # (x' -> f(x, y))
    # []
    # []
    # argumentCount = 0
    # (x' -> f(x, y))
    
    # [0]
    # [2, 2, 0, 0, 2, 0, 0]
    # [x]
    # [f, f, x, y, f, y, z]
    # argumentAmount = 0
    # []
    
    # [0] -> [], [x] -> [], newVar = "x"
    
    # newTerm = "f("
    # [2, 0, 0, 2, 0, 0]
    # [f, x, y, f, y, z]
    # argumentAmount = 1
    # [2]
    
    # newTerm = "f(f("
    # [0, 0, 2, 0, 0]
    # [x, y, f, y, z]
    # argumentAmount = 2
    # [1, 2]
    
    # newTerm = "f(f(x,"
    # [0, 2, 0, 0]
    # [y, f, y, z]
    # argumentAmount = 1
    # [1, 1]
    
    # newTerm = "f(f(x,y),"
    # [2, 0, 0]
    # [f, y, z]
    # argumentAmount = 0
    # [1, 0]
    
    # newTerm = "f(f(x, y), f("
    # [0, 0]
    # [y, z]
    # argumentAmount = 1
    # [0, 2]
    
    # newTerm = "f(f(x, y), f(y, "
    # [0]
    # [z]
    # argumentAmount = 0
    # [0, 1]
    
    # newTerm = "f(f(x, y), f(y, z))"
    # []
    # []
    # argumentAmount = -1
    # [0, 0]
    
    inputList = ChangeTreeToList(CreateTree(substitution[0]))
    
    inputArgumentList = ModifyListToArgumentList(inputList)
    termArgumentList = ModifyListToArgumentList(term)
    
    print(f"Input argument list: {inputArgumentList}")
    print(f"Term argument list: {termArgumentList}")
    
    flatInput = FlattenList(inputList)
    flatTerm = FlattenList(term)
    rulesSet = set([])
    argumentCount = 0
    
    while inputArgumentList != [] and termArgumentList != []:
        argumentCount += inputArgumentList[0]
        argumentCount -= 1
        
        if inputArgumentList[0] == 0:
            newVar = flatInput[0]
            newTerm = ""
            closeBracketNow = []
            
            argumentAmount = 0
            while argumentAmount >= 0:
                if len(flatTerm) != 0:
                    newTerm += flatTerm[0]
                
                if len(termArgumentList) != 0 and termArgumentList[0] != 0:
                    newTerm += "("
                    argumentAmount += termArgumentList[0]
                    closeBracketNow.append(termArgumentList[0])
                    
                    if len(closeBracketNow) >= 2:
                        closeBracketNow[-2] -= 1
                elif len(closeBracketNow) >= 1:
                    closeBracketNow[-1] -= 1
                    while closeBracketNow[-1] == 0:
                        newTerm += ")"
                        closeBracketNow.pop()
                        
                        if len(closeBracketNow) == 0:
                            break
                    
                    if len(closeBracketNow) >= 1 and closeBracketNow[-1] > 0:
                        newTerm += ","
                    
                argumentAmount -= 1 
                if len(flatTerm) != 0:
                    flatTerm = flatTerm[1:]
                    termArgumentList = termArgumentList[1:]
            
            rulesSet.add((newVar, newTerm))
            
            inputArgumentList = inputArgumentList[1:]
            flatInput = flatInput[1:]
            continue
        
        inputArgumentList = inputArgumentList[1:]
        termArgumentList = termArgumentList[1:]
        flatInput = flatInput[1:]
        flatTerm = flatTerm[1:]
    
    rules = {}
    for rule in rulesSet:
        rules[rule[0]] = [rule[1]]
    
    rules = Unification(rules)
    # print(rules)
    newSubstitutionInput = ChangeTreeToList(CreateTree(substitution[0]))
    newSubstitutionOutput = ChangeTreeToList(CreateTree(substitution[1]))
    
    for key, value in rules.items():
        newInput = ApplySubstitutionRecursive((key, value[0]), newSubstitutionInput)
        newOutput = ApplySubstitutionRecursive((key, value[0]), newSubstitutionOutput)
        if newInput != None:
            newSubstitutionInput = newInput
        
        if newOutput != None:
            newSubstitutionOutput = newOutput
    
    newSubstitution = (CreateInputStringFromTree(ChangeListToTree(newSubstitutionInput)), 
                        CreateInputStringFromTree(ChangeListToTree(newSubstitutionOutput)))
    
    print(f"New substituion: {newSubstitution}")
    return ApplySubstitutionRecursive(newSubstitution, term)


def TermIsVariable(term : List) -> bool:
    variables = LoadVariables()
    if len(term) == 1 and term[0] in variables:
        return True
    
    return False


def Unification(substitutions : Dict[str, List]) -> Optional[Dict[str, List]]:
    times = 1000
    while True:
        initial_substitutions = {}
        for key, value in substitutions.items():
            initial_substitutions[key] = []
            for entry in value:
                initial_substitutions[key].append(entry)
        
        substitutions = RuleDeleteSubstitutions(substitutions)
        # print(f"After deletion: {substitutions}")
        substitutions = RuleDecomposeSubstitutions(substitutions)
        # print(f"After decomposition: {substitutions}")
        substitutions = RuleOrientSubstitutions(substitutions)
        # print(f"After orientation: {substitutions}")
        substitutions = RuleEliminateSubstitutions(substitutions)
        # print(f"After elimination: {substitutions}")
        
        if initial_substitutions == substitutions:
            return substitutions
        
        if times == 0:
            break
        
        times -= 1
        
    return None

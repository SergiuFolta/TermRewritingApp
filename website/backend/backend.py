from typing import Optional, List
from flask import flash
from .variables import *
from .functions import *
from .node import Node
from .representation_changes import *
from .substitutions import *
from .database import *


def CountArguments(function_str: str) -> int:
    """
        This function counts the number of arguments a function has.
    Args:
        function_str (str): the remainder of the input string after the function character was found e.g
                            f(x, y) would mean function_str = "(x, y)"

    Returns:
        int: number of arguments this function has. returns -1 if it's an invalid string
    """
    function_str = function_str.replace(" ", "")
    arguments = 0 # assume this is a constant function
                    
    open_brackets = 1
    i = 0
    while (i < len(function_str) and open_brackets > 0):
        i += 1
        if function_str[i] == "," and open_brackets == 1: # we're accepting another argument for this function
            arguments += 1
        elif function_str[i] == "(":
            open_brackets += 1
        elif function_str[i] == ")":
            open_brackets -= 1
        elif arguments == 0: # if this is not ",", "(" or ")" and arguments is 0, this means this is not a constant function as we assumed
            arguments = 1
        
    return arguments if open_brackets == 0 else -1


# def LoadLanguage(input_str: str) -> None:
#     """
#         This function takes in a string argument and loads the 
#         found functions and variables into their respective objects.
#     Args:
#         input_str (str): term to load the language from
#     """
#     functions = LoadFunctions()
#     variables = LoadVariables()
    
#     i = 0
#     while i < len(input_str):
#         if input_str[i] not in "(), ":
#             term = input_str[i]
#             while i + 1 < len(input_str) and input_str[i + 1] not in "(), ":
#                 i += 1
#                 term += input_str[i]
            
#             check = i
#             while check + 1 < len(input_str) and input_str[check + 1] == " ":
#                 check += 1
#                 pass
                
#             if i + 1 == len(input_str): # this should just be an atomic variable
#                 if len(variables) + len(functions) == 0: # this should be the ONLY term
#                     variables.add(term)
#                 else:
#                     flash("ERROR: String invalid. It ends with a term, but it's not an atomic term.", category='error')
#                     return
            
#             if check != i and input_str[check + 1] not in ",)":
#                 flash("ERROR: You either need a comma between variables in the same function or to close the function.", category="error")
#                 return
                
#             if term not in variables and term not in functions:
#                 next_char_index = input_str.find("(", i + 1)
#                 if next_char_index == -1: # this is certainly a variable
#                     variables.add(term)
#                 elif input_str[i + 1:next_char_index].count(" ") != (next_char_index - (i + 1)): 
#                     # if there aren't just whitespaces, then the "(" is most likely from another function. Assume this is a variable
#                     variables.add(term)
#                     continue
                
#                 if input_str[next_char_index] == "(": # this has to be a function
#                     functions[term] = CountArguments(input_str[next_char_index:])
                    
#                     if functions[term] == -1:
#                         flash(f"ERROR: String is invalid, couldn't determine number of arguments for function {term}!", category='error')
#                         return
#                 else: # this is a variable
#                     variables.add(term)
#             elif term in functions:
#                 next_char_index = input_str.find("(", i + 1)
#                 if next_char_index == -1:
#                     flash(f"ERROR: {term} found again, should be a function but is now a variable."
#                             , category='error')
#                     return
#                 elif functions[term] == 0 and input_str[i + 1:next_char_index].count(" ") != (next_char_index - (i + 1)): 
#                     # if there aren't just whitespaces, then the "(" is most likely from another function. 
#                     # Assume this is a constant function that was previously written with "()" notation
#                     i += 1
#                     continue
                    
#                 if input_str[next_char_index] == "(": # this has to be a function
#                     arguments = CountArguments(input_str[next_char_index:])
                    
#                     if arguments != functions[term]:
#                         flash(f"ERROR: Function {term} found again, taking a different number of arguments than before! \
#                                 Found {functions[term]} before, now found {arguments}.", category='error')
#                         return
#                 else: # this was previously recognized as a function, but is now a variable
#                     flash(f"ERROR: {term} was previously a function, but is a variable in this term!", category="error")
#                     return
#             elif term in variables:
#                 next_char_index = input_str.find("(", i + 1)
#                 if input_str[i + 1:next_char_index].count(" ") == (next_char_index - (i + 1)):
#                     # this means this is a function in our string, but was previously a variable
#                     flash(f"ERROR: {term} found again, should be a variable but is now a function." , category='error')
#                     return
        
#         i += 1
    
#     SaveFunctions(functions)
#     SaveVariables(variables)


def PrintTree(head: Node, spacing: int = 2, current_level: int = 0) -> str:
    """
    This function takes in the head of a tree and prints the content out to the console.

    Args:
        head (Node): head of the tree you want to display
        spacing (int): how many whitespaces and dash characters should be used when displaying a new line (has to be > 0)
        current_level (int): the current level of the tree (this shouldn't be given as a parameter on the first call)

    Returns:
        str: returns the list representation as a string
    """
    tree_repr = ""
    
    if spacing <= 0:
        raise ValueError("spacing must be greater than 0")

    stack = [(head, current_level, "0")]
    while stack:
        node, level, node_pos = stack.pop()

        if node == None:
            flash("ERROR: Could not create tree.", category="error")
            return
        
        tree_repr += (' ' * (spacing + 1) * (level - 1) + ('+' + '-' * spacing) * (level > 0) + node.value) + \
                        (f" ({node_pos})" if node != head else "") + '\n'

        if node.next != None:
            node_pos += "_0" if node != head else ""
            for child in node.next:  # Iterate through children
                node_pos = node_pos[:node_pos.rfind("_") + 1] + str(int(node_pos[node_pos.rfind("_") + 1:]) + 1)
                stack.append((child, level + 1, node_pos))
                
            stack[len(stack) - len(node.next):] = reversed(stack[len(stack) - len(node.next):])
        
    return tree_repr


def GetPositionFromListIndex(term: List, index: int) -> str:
    """
    This function takes in an index from the term (imagine it as one long non-nested list)
    and returns the position of the element taking into consideration our nested list encoding.

    Args:
        term (List): list representing a term
        index (int): the index of the subterm we'd like to get 

    Returns:
        str: position of the subterm you'd like to get (in format "{number}_{number}_{number}").
                If you want to get the root, position is = ""
    """
    position = ""
    
    if index == 0:
        return position
    
    term = term[1:]
    if len(term) == 1:
        term = term[0]
    
    while index != 0:
        curr_position = 0
        for item in term:
            if type(item) == list:
                flatList = FlattenList(item)
                
                if len(flatList) < index:
                    index -= len(flatList)
                else:
                    position += f"_{str(curr_position)}"
                    term = item
                    break
            else:
                curr_position += 1
                index -= 1
                
                if index == 0:
                    position += f"_{str(curr_position)}"
                    break
    
    return position[1:] # Skip the first character, which will always be _


def GetSubtermAtPosition(term: List, position: str = "") -> List:
    """
    This function takes in a position from the term and returns the subterm from
    that position onward.

    Args:
        term (List): list representing a term
        position (str): position of the subterm you'd like to get (in format "{number}_{number}_{number}").
                        If you want to get the root, position is = ""

    Returns:
        List: returns the list of lists or [] if there's an error
    """
    if position == "":
        return term
    
    indeces = position.split("_")
    
    for index in indeces:
        if len(term) == 1:
            flash(f"Couldn't find element at position {position}. Stopped at {index}.", category="error")
            return []
        
        index = int(index)
        term_args = term[1]

        subterms = []
        i = 0
        while i < len(term_args):
            if i + 1 == len(term_args): # last element
                subterms.append([term_args[i]])
                i += 1
            elif type(term_args[i + 1]) == list: # this is a function
                subterms.append([term_args[i], term_args[i + 1]])
                i += 2
            else: # this is a variable (or a constant function)
                subterms.append([term_args[i]])
                i += 1

        if index > len(subterms):
            flash(f"ERROR: There are not enough subterms for index {index}!", category="error")
            return []
        
        term = subterms[index - 1]
        
    return term


def ReplaceSubtermAtPosition(original_term: List, replacement_term: List, position: str = "") -> List:
    """
    This function takes in a position from {original_term} and returns a new term created from replacing
    everything from {position} in {original_term} with {replacement_term}.
    This function does NOT modify {original_term} outside of its scope.
    
    Args:
        original_term (List): list representing a term which will be built on top of
        replacement_term (List): list representing a term which will replace a subterm from {original_term}
        position (str): position of the subterm you'd like to get (in format "{number}_{number}_{number}").
                        If you want to get the root, position is = ""

    Returns:
        List: returns the new term after replacement
    """
    if position == "":
        return replacement_term
    
    indeces = position.split("_")
    
    head = ChangeListToTree(original_term)
    
    # f(f(f(x', y'), z'), z)
    # f(f(x', y'), f(z', z))
    # 1
    
    curr_node = head
    for i in range(0, len(indeces)):
        index = int(indeces[i]) - 1
        if curr_node.next != None:
            curr_node = curr_node.next[index] # f(f(x', y'))
        else:
            flash(f"ERROR: Cannot replace subterm at index {index + 1}! The position {position} doesn't exist.", category="error")
            return []
    
    curr_node.previous.next[int(indeces[-1]) - 1] = ChangeListToTree(replacement_term)
    
    new_term = ChangeTreeToList(head)
    
    return new_term


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


def TermIsVariable(term : List) -> bool:
    variables = LoadVariables()
    
    if len(term) == 1 and term[0] in variables:
        return True
    
    return False


def LexicographicPathOrdering(term1: List, term2: List) -> int:
    # s = term1
    # t = term2
    # print(f"Term 1 = {term1}, Term2 = {term2}")
    if term1 == term2:
        return 0
    
    flat_term1 = FlattenList(term1)
    
    # print("In LPO1")
    # LPO1
    if TermIsVariable(term2):
        if term2[0] in flat_term1:
            return 1
        else:
            return -1
    
    if TermIsVariable(term1):
        return -1
        
    # print("In LPO2a")
    # LPO2
    # LPO2a)
    precedences = {"i": 2, "f": 1, "e": 0}
    subterms1 = []
    i = 0
    if len(term1) == 1: # constant function
        return -1
    
    term1_args = term1[1]
    while i < len(term1_args):
        if i + 1 == len(term1_args): # last element
            subterms1.append([term1_args[i]])
            i += 1
        elif type(term1_args[i + 1]) == list: # this is a function
            subterms1.append([term1_args[i], term1_args[i + 1]])
            i += 2
        else: # this is a variable
            subterms1.append([term1_args[i]])
            i += 1
    
    # print(f"Subterms of term 1: {subterms1}")

    for subterm in subterms1:
        value = LexicographicPathOrdering(subterm, term2)
        if value == 0 or value == 1:
            return 1
    
    # print("In LPO2b")
    # LPO2b)
    subterms2 = []
    i = 0
    if len(term2) == 1: # constant function
        if precedences[term1[0]] > precedences[term2[0]]:
            return 1
        else:
            return -1
    
    term2_args = term2[1]
    while i < len(term2_args):
        if i + 1 == len(term2_args): # last element
            subterms2.append([term2_args[i]])
            i += 1
        elif type(term2_args[i + 1]) == list: # this is a function
            subterms2.append([term2_args[i], term2_args[i + 1]])
            i += 2
        else: # this is a variable (or a constant function)
            subterms2.append([term2_args[i]])
            i += 1
    
    # print(f"Subterms of term 2: {subterms2}")
    
    if precedences[term1[0]] > precedences[term2[0]]:
        found = False
        for subterm in subterms2:
            if LexicographicPathOrdering(term1, subterm) == -1:
                found = True
                break
        
        if not found:
            return 1
            
    # print("In LPO2c")
    # LPO2c)
    if precedences[term1[0]] == precedences[term2[0]]:
        for subterm in subterms2:
            if LexicographicPathOrdering(term1, subterm) == -1:
                return -1
        
        for i in range(len(subterms1)):
            value = LexicographicPathOrdering(subterms1[i], subterms2[i])
            if value == 0:
                continue
        
            if value == 1:
                return 1
            
            if value == -1:
                return -1
    
    return -1

# Critical Pair functions
def GetAllFunctionPositions(term: List) -> List[str]:
    if TermIsVariable(term):
        return []
    
    positions = []
    
    flatTerm = FlattenList(term)
    functions = LoadFunctions()
    
    for i in range(len(flatTerm)):
        if flatTerm[i] in functions.keys():
            positions.append(GetPositionFromListIndex(term, i))
    
    return positions


def GetUniqueVariables(term: List) -> List:
    variables = []
    
    term = FlattenList(term)
    for subterm in term:
        if TermIsVariable([subterm]):
            if subterm not in variables:
                variables.append(subterm)
    
    return variables


def ReplaceCoincidingVariables(vars1: List, vars2: List, term: List, rule: Tuple[str, str]) -> Tuple[List, Tuple[str, str]]:
    nonuniqueVars = []
    for var in vars1:
        if var in vars2:
            nonuniqueVars.append(var)
    
    varRules = {}
        
    variables = LoadVariables()
    flatTerm = FlattenList(term)

    for var in nonuniqueVars:
        newVarName = var + "'"
        while newVarName in flatTerm or newVarName in varRules.keys():
            newVarName += "'"
        
        varRules[var] = newVarName
        if newVarName not in variables:
            AddVariable(newVarName, False)
    
    newTerm = ChangeTreeToList(ChangeListToTree(term))
    newSubstitutionInput = ChangeTreeToList(CreateTree(rule[0]))
    newSubstitutionOutput = ChangeTreeToList(CreateTree(rule[1]))
    
    for key, value in varRules.items():
        newTerm = ApplySubstitutionRecursive((key, value), newTerm)
        inputRes = ApplySubstitutionRecursive((key, value), newSubstitutionInput)
        if inputRes != None:
            newSubstitutionInput = inputRes
            
        outputRes = ApplySubstitutionRecursive((key, value), newSubstitutionOutput)
        if outputRes != None:
            newSubstitutionOutput = outputRes
            
    newSubstitution = (CreateInputStringFromTree(ChangeListToTree(newSubstitutionInput)), 
                        CreateInputStringFromTree(ChangeListToTree(newSubstitutionOutput)))
    
    return(newTerm, newSubstitution)


def GetCriticalPair(term1: List, term2: List, rule1: Tuple[str, str], rule2: Tuple[str, str], position: str) -> Tuple[List, List]:
    # find most general unifier between {term1} at position {position} and {term2}
    rules = {}
    
    subterm1 = GetSubtermAtPosition(term1, position)
    functionArity = LoadFunctions()[subterm1[0]]
    for i in range(functionArity):
        lhs = CreateInputStringFromTree(ChangeListToTree(GetSubtermAtPosition(subterm1, f"{i + 1}")))
        rhs = CreateInputStringFromTree(ChangeListToTree(GetSubtermAtPosition(term2, f"{i + 1}")))
        
        if lhs in rules.keys():
            rules[lhs].append(rhs)
        else:
            rules[lhs] = [rhs]
        
    # print(f"Before unification: {rules}")
    
    rules = Unification(rules)
    
    # print(f"After unification: {rules}")
    
    for lhs in rules.keys():
        for rhs in rules[lhs]:
            result = ApplySubstitutionRecursive((lhs, rhs), term1)
            if result != None:
                term1 = result
    
    # print(f"Term1 after applying all rules: {term1}")
    
    subterm1AfterUnification = GetSubtermAtPosition(term1, position)

    critPair1Res = [ApplySubstitution(rule1, term1)]
    critPair2Res = [ApplySubstitution(rule2, subterm1AfterUnification)]
    
    # critPair1Res = []
    # critPair2Res = []
    
    # functionPositions = GetAllFunctionPositions(term1)
    
    # for functionPosition in functionPositions:
    #     subterm = GetSubtermAtPosition(term1, functionPosition)
    #     if subterm[0] != term2[0]:
    #         continue
        
    #     critPair1Res.append(ApplySubstitution(rule1, subterm))
    #     critPair2Res.append(ApplySubstitution(rule2, subterm))
    
    # print(f"CritPair1Res = {critPair1Res}")
    # print(f"CritPair2Res = {critPair2Res}")
    
    critPair1Res = [pair for pair in critPair1Res if pair != None]
    critPair2Res = [pair for pair in critPair2Res if pair != None]
    
    if len(critPair1Res) == 0 or len(critPair2Res) == 0:
        return (None, None)
    
    critPair1 = critPair1Res[-1]
    critPair2 = critPair2Res[-1]
    
    # print(f"Crit Pair 1 before mgu: {critPair1}")
    # print(f"Crit Pair 2 before mgu: {critPair2}")
    
    # apply mgu on the first result
    # for lhs in rules.keys():
    #     for rhs in rules[lhs]:
    #         result = ApplySubstitutionRecursive((lhs, rhs), critPair1)
    #         if result != None:
    #             critPair1 = result
    #             print("applied mgu on critpair1")
            
    # apply mgu on the second result
    # for lhs in rules.keys():
    #     for rhs in rules[lhs]:
    #         result = ApplySubstitutionRecursive((lhs, rhs), critPair2)
    #         if result != None:
    #             critPair2 = result
    #             print("applied mgu on critpair2")
    
    # print(f"Crit Pair 2 before replacement: {critPair2}")
    # replace the subterm at position {position} in {term1} with {critPair2}
    critPair2 = ReplaceSubtermAtPosition(term1, critPair2, position)
    
    # print(f"Critical pair 1: {critPair1}") # f(y', z') ->               ["f", ["y'", "z'"]]
    # print(f"Critical pair 2: {critPair2}") # f(y', f(f(y', z'), z)) ->  ["f", ["y'", "f", ["f", ["y'", "z'"], "z"]]]

    return (critPair1, critPair2)


def GenerateAllCriticalPairs(rules: List, combinations: List) -> List[Tuple[List, List]]:
    # print(rules)
    critPairs = []
    for combination in combinations:
        term1 = ChangeTreeToList(CreateTree(rules[combination[0]][0])) # left hand side of rule
        original_term2 = ChangeTreeToList(CreateTree(rules[combination[1]][0])) # right hand side of rule
        
        # replace all coinciding variables in term2 and reflect changes in rule2 with newRule
        term2, newRule = ReplaceCoincidingVariables(GetUniqueVariables(term1), GetUniqueVariables(original_term2), original_term2, rules[combination[1]])
        
        positions = GetAllFunctionPositions(term1)
        
        for position in positions:
            if term1 == original_term2 and position == "":
                continue
        
            # print(f"----------------------------------------------------------------------------------------\n \
            #     Attempting to find critical pair for:\n \
            #     Term 1: {term1}\n \
            #     Term 2: {term2}\n \
            #     Rule 1: {rules[combination[0]]}\n \
            #     Rule 2: {newRule}\n \
            #     Position: {position}")
            
            if GetSubtermAtPosition(term1, position)[0] != term2[0]:
                # print(f"Functions have different number of arguments!")
                continue
            
            critPair = GetCriticalPair(
                term1,
                term2,
                rules[combination[0]],
                newRule,
                position
            )
        
            if critPair != (None, None) and critPair[0] != critPair[1]:
                newRuleInput = CreateInputStringFromTree(ChangeListToTree(critPair[0]))
                newRuleOutput = CreateInputStringFromTree(ChangeListToTree(critPair[1]))
                
                with open("out.txt", "a") as f:
                    f.write(f"Added critical pair {(newRuleInput, newRuleOutput)} to the set of identities.\n")
                critPairs.append(critPair)
    
    return critPairs


def ReplaceCoincidingVariablesCritPair(vars1: List, vars2: List, term: List) -> Tuple[List, Dict[str, str]]:
    nonuniqueVars = []
    for var in vars1:
        if var in vars2:
            nonuniqueVars.append(var)
    
    varRules = {}
        
    variables = LoadVariables()
    flatTerm = FlattenList(term)

    for var in nonuniqueVars:
        tempVar = var
        yes = True
        while tempVar in flatTerm or tempVar in varRules.values():
            if "'" in tempVar:
                tempVar = tempVar[:(len(tempVar) - 1)]
            else:
                if tempVar in flatTerm or tempVar in varRules.values():
                    yes = False
                    break
        
        if yes:
            varRules[var] = tempVar
            if tempVar not in variables:
                AddVariable(tempVar, False)
        
        newVarName = var + "'"
        while newVarName in flatTerm or newVarName in varRules.values():
            newVarName += "'"
        
        varRules[var] = newVarName
        if newVarName not in variables:
            AddVariable(newVarName, False)
    
    newTerm = ChangeTreeToList(ChangeListToTree(term))
    
    for key, value in varRules.items():
        newTerm = ApplySubstitutionRecursive((key, value), newTerm)
    
    return (newTerm, varRules)


def RenameVariablesInCritPair(term1: List, term2: List) -> Tuple[List, List]:
    variableOrder = ["x", "y", "z", "x'", "y'", "z'", "w", "a", "b", "c", "d", "g"]
    vars1 = GetUniqueVariables(term1)
    vars2 = GetUniqueVariables(term2)
    maxLen = max(len(vars1), len(vars2))
    maxVars = vars1 if maxLen == len(vars1) else vars2
    minVars = vars2 if maxLen == len(vars1) else vars1
    
    rules = []
    if maxLen > len(variableOrder):
        print(f"Vars1 = {term1}")
        print(f"Vars2 = {term2}")
        print(f"HEY I NEED MORE VARIABLES OVER HERE!!!!11!!!1!!!!!!!!1!1!!")
        return []
    
    # index = 0
    # thisIsFineIamFine = True
    # for var in maxVars:
    #     if var == variableOrder[index]:
    #         index += 1
    #     else:
    #         thisIsFineIamFine = False
    
    # if thisIsFineIamFine:
    #     return (term1, term2)
    # f(x', f(y, z))
    # ["x'", "y", "z"]
    # ["x",  "y", "z", "w", "a", "b", "c", "d", "e"]
    # rename all variables such that they don't coincide anymore with anything
    # for each variable in order, we assign a new variable from the ordering above
    # ???
    # profit
    
    newTerm1 = ChangeTreeToList(ChangeListToTree(term1))
    newTerm2 = ChangeTreeToList(ChangeListToTree(term2))
    
    flatList1 = FlattenList(newTerm1)
    flatList2 = FlattenList(newTerm2)
    
    variables = vars1.copy()
    for var in vars2:
        if var not in variables:
            variables.append(var)
    
    knownVariables = LoadVariables()
    varRules = {}
    newVariables = []
    for var in variables:
        newVarName = var + "'"
        while newVarName in flatList1 or newVarName in flatList2 or newVarName in variableOrder or newVarName in varRules.values():
            newVarName += "'"
        
        if newVarName not in knownVariables:
            AddVariable(newVarName, False)

        varRules[var] = newVarName
        newVariables.append(newVarName)
    
    # print(f"Var rules: {varRules}")
    # print(f"Newterm2: {newTerm2}")
    for input, output in varRules.items():
        value1 = ApplySubstitutionRecursive((input, output), newTerm1)
        value2 = ApplySubstitutionRecursive((input, output), newTerm2)
        
        if value1 != None:
            newTerm1 = value1
            
        if value2 != None:
            newTerm2 = value2
            # print(f"NewNewterm2: {newTerm2}")
    
    for index, var in enumerate(newVariables):
        rules.append((var, variableOrder[index]))
    # print(f"Rules: {rules}")
    # i = 0
    # while i < len(maxVars):
    #     if maxVars[i] in variableOrder:
    #         variableOrder.remove(maxVars[i])
            
    #     i += 1
    
    # for i in range(len(maxVars)):
    #     rules.append((maxVars[i], variableOrder[i]))
    
    # newTerm1 = ChangeTreeToList(ChangeListToTree(term1))
    # newTerm2 = ChangeTreeToList(ChangeListToTree(term2))
    
    # print(f"Newterm2: {newTerm2}")
    for rule in rules:
        value1 = ApplySubstitutionRecursive(rule, newTerm1)
        value2 = ApplySubstitutionRecursive(rule, newTerm2)
        
        if value1 != None:
            newTerm1 = value1
            
        if value2 != None:
            newTerm2 = value2
            # print(f"NewNewterm2: {newTerm2}")
        
    return (newTerm1, newTerm2)


def DetermineCompleteness(identities: List, times: int = 1000) -> Tuple[bool, List]:
    prevRules = []
    currRules = []
    identityList = identities.copy()
    
    i = 0
    while i < len(identityList):
        identity = identityList[i] # take the current identity
        term1 = ChangeTreeToList(CreateTree(identity[0])) # take left hand side of identity (s)
        term2 = ChangeTreeToList(CreateTree(identity[1])) # take right hand side of identity (t)
        print(identity)
        if term1 == term2: # if s == t
            identities.remove(identity)
        elif LexicographicPathOrdering(term1, term2) == 1: # if s > t
            identities.remove(identity)
            newRuleInput = CreateInputStringFromTree(ChangeListToTree(term1))
            newRuleOutput = CreateInputStringFromTree(ChangeListToTree(term2))
            
            if (newRuleInput, newRuleOutput) not in currRules:
                currRules.append((newRuleInput, newRuleOutput))
        elif LexicographicPathOrdering(term2, term1) == 1: # if t > s
            identities.remove(identity)
            newRuleInput = CreateInputStringFromTree(ChangeListToTree(term2))
            newRuleOutput = CreateInputStringFromTree(ChangeListToTree(term1))
            
            if (newRuleInput, newRuleOutput) not in currRules:
                currRules.append((newRuleInput, newRuleOutput))
        else:
            return (False, currRules)
        
        i += 1
    
    print(f"Rules before critical pairs: {currRules}")
    
    while currRules != prevRules:
        prevRules = currRules.copy()
        
        print(f"Prev Rules = {prevRules}")
        numOfRules = len(prevRules)
        combos = []
        for i in range(numOfRules):
            for j in range(numOfRules):
                combos.append((i, j))
        
        # compute all critical pairs under our rule set prevRules
        critPairs = GenerateAllCriticalPairs(prevRules, combos)
        print(f"Crit Pairs = {critPairs}")
        
        # reduce all critical pairs to normal form under our rule set prevRules
        for critPair in critPairs:
            term1 = critPair[0]
            term2 = critPair[1]
            
            normalFormTerm1 = ChangeTreeToList(ChangeListToTree(term1))
            normalFormTerm2 = ChangeTreeToList(ChangeListToTree(term2))
                
            ruleIndex = 0
            while ruleIndex < len(currRules):
                rule = currRules[ruleIndex]
                # print(f"For rule: {rule} we now have terms {normalFormTerm1} and {normalFormTerm2}")
                ruleInput = rule[0]
                ruleOutput = rule[1]
                
                changed = False
                while term1 != None or term2 != None:
                    term1 = ApplySubstitution((ruleInput, ruleOutput), normalFormTerm1)
                    term2 = ApplySubstitution((ruleInput, ruleOutput), normalFormTerm2)
                    
                    if term1 != None:
                        # print(f"Changed normal form of term1 from {normalFormTerm1} to {term1} with rule {rule}")
                        normalFormTerm1 = term1
                        changed = True

                    if term2 != None:
                        # print(f"Changed normal form of term2 from {normalFormTerm2} to {term2} with rule {rule}")
                        normalFormTerm2 = term2
                        changed = True
                
                if changed:
                    ruleIndex = -1
                # if ruleInput == "f(y, y)" and identity[0] == 'i(f(i(y), i(f(i(f(x, i(y))), x))))':
                #     return None
                
                term1 = ChangeTreeToList(CreateTree(identity[0]))
                term2 = ChangeTreeToList(CreateTree(identity[1]))
                ruleIndex += 1
            
            foundAlready = False
            newNormalForms = RenameVariablesInCritPair(normalFormTerm1, normalFormTerm2)
            normalFormTerm1 = newNormalForms[0]
            normalFormTerm2 = newNormalForms[1]
            newNormalForms = (CreateInputStringFromTree(ChangeListToTree(newNormalForms[0])),
                                CreateInputStringFromTree(ChangeListToTree(newNormalForms[1])))
            for rule in currRules:
                if (newNormalForms[0], newNormalForms[1]) == rule or (newNormalForms[1], newNormalForms[0]) == rule:
                    foundAlready = True
                    break
            
            newPair = (normalFormTerm1, normalFormTerm2)
            
            if LexicographicPathOrdering(newPair[0], newPair[1]) == 1: # if critPair1 > critPair2, then currRules += (critPair1, critPair2)
                newRuleInput = CreateInputStringFromTree(ChangeListToTree(newPair[0]))
                newRuleOutput = CreateInputStringFromTree(ChangeListToTree(newPair[1]))
                
                if (newRuleInput, newRuleOutput) not in currRules:
                    currRules.append((newRuleInput, newRuleOutput))
            elif LexicographicPathOrdering(newPair[1], newPair[0]) == 1: # if critPair2 > critPair1, then currRules += (critPair2, critPair1)
                newRuleInput = CreateInputStringFromTree(ChangeListToTree(newPair[1]))
                newRuleOutput = CreateInputStringFromTree(ChangeListToTree(newPair[0]))
                
                if (newRuleInput, newRuleOutput) not in currRules:
                    currRules.append((newRuleInput, newRuleOutput))
            elif newPair[0] != newPair[1]:
                # print(f"Failed at pair with rules {prevRules}:\noldPair: {oldPair}\nnewPair: {newPair}")
                return (False, currRules) # if there is one critical pair in normal form which cannot be ordered, fail
        
        times -= 1
        
        if times == 0:
            print(f"This has been going on for too long.")
            return (False, currRules)

    print(f"Rules after critical pairs: {currRules}")

    return (True, currRules)


def DetermineCompletenessHuet(identities: List, maxTimes: int = 1000) -> Tuple[bool, List]:
    # Initialization
    currIdentities = identities.copy() # E_i
    nextIdentities = [] # E_i+1
    
    currRules = [] # R_i
    nextRules = [] # R_i+1
    ruleMarkings = []
    
    i = 0
    
    times = 0
    while (len(currIdentities) > 0 or False in ruleMarkings) and times < maxTimes:
        # print(f"Run {times}:\n\tcurrIdentities: {currIdentities}\n\tcurrRules: {currRules}")
        while len(currIdentities) > 0:
            # a)
            identity = currIdentities[0]
            # print(f"Looking at identity: {identity}")
            
            # b)
            term1 = ChangeTreeToList(CreateTree(identity[0]))
            term2 = ChangeTreeToList(CreateTree(identity[1]))
            
            normalFormTerm1 = ChangeTreeToList(ChangeListToTree(term1))
            normalFormTerm2 = ChangeTreeToList(ChangeListToTree(term2))
                
            ruleIndex = 0
            while ruleIndex < len(currRules):
                rule = currRules[ruleIndex]
                # print(f"For rule: {rule} we now have terms {normalFormTerm1} and {normalFormTerm2}")
                ruleInput = rule[0]
                ruleOutput = rule[1]
                
                changed = False
                while term1 != None or term2 != None:
                    term1 = ApplySubstitution((ruleInput, ruleOutput), normalFormTerm1)
                    term2 = ApplySubstitution((ruleInput, ruleOutput), normalFormTerm2)
                    
                    if term1 != None:
                        # print(f"Changed normal form of term1 from {normalFormTerm1} to {term1} with rule {rule}")
                        normalFormTerm1 = term1
                        changed = True

                    if term2 != None:
                        # print(f"Changed normal form of term2 from {normalFormTerm2} to {term2} with rule {rule}")
                        normalFormTerm2 = term2
                        changed = True
                
                if changed:
                    ruleIndex = -1
                # if ruleInput == "f(y, y)" and identity[0] == 'i(f(i(y), i(f(i(f(x, i(y))), x))))':
                #     return None
                
                term1 = ChangeTreeToList(CreateTree(identity[0]))
                term2 = ChangeTreeToList(CreateTree(identity[1]))
                ruleIndex += 1
            
            foundAlready = False
            newNormalForms = RenameVariablesInCritPair(normalFormTerm1, normalFormTerm2)
            normalFormTerm1 = newNormalForms[0]
            normalFormTerm2 = newNormalForms[1]
            newNormalForms = (CreateInputStringFromTree(ChangeListToTree(newNormalForms[0])),
                                CreateInputStringFromTree(ChangeListToTree(newNormalForms[1])))
            for rule in currRules:
                if (newNormalForms[0], newNormalForms[1]) == rule or (newNormalForms[1], newNormalForms[0]) == rule:
                    foundAlready = True
                    break
            
            # c)
            if normalFormTerm1 == normalFormTerm2 or foundAlready:
                nextRules = currRules.copy()
                
                nextIdentities = currIdentities.copy()
                nextIdentities.remove(identity)
                
                i += 1
                currRules = nextRules.copy()
                currIdentities = nextIdentities.copy()
            # d)
            else:
                lpo1 = LexicographicPathOrdering(normalFormTerm1, normalFormTerm2)
                lpo2 = LexicographicPathOrdering(normalFormTerm2, normalFormTerm1)
                
                if lpo1 != 1 and lpo2 != 1:
                    print(f"Failed at identity with normal forms: {normalFormTerm1}, {normalFormTerm2}")
                    print(f"Failed with rules {nextRules} and identities {nextIdentities}.")
                    return (None, nextRules)
                # e)
                else:
                    if lpo2 == 1:
                        aux = ChangeTreeToList(ChangeListToTree(normalFormTerm1))
                        normalFormTerm1 = ChangeTreeToList(ChangeListToTree(normalFormTerm2))
                        normalFormTerm2 = ChangeTreeToList(ChangeListToTree(aux))
                    
                    normalFormTermInput = CreateInputStringFromTree(ChangeListToTree(normalFormTerm1))
                    normalFormTermOutput = CreateInputStringFromTree(ChangeListToTree(normalFormTerm2))
                    
                    nextRules = currRules.copy()
                    index = 0
                    while index < len(nextRules):
                        newRule = nextRules[index]
                        
                        checkInput = ChangeTreeToList(CreateTree(newRule[0]))
                        newInput = ChangeTreeToList(CreateTree(newRule[0]))
                        
                        tempInput = ApplySubstitution((normalFormTermInput, normalFormTermOutput), newInput)

                        if tempInput != None:
                            newInput = tempInput
                        
                        if checkInput == newInput:
                            newOutput = ChangeTreeToList(CreateTree(newRule[1]))
                            tempOutput = ChangeTreeToList(CreateTree(newRule[1]))
                            
                            tempRules = currRules.copy()
                            tempRules.append((normalFormTermInput, normalFormTermOutput))
                            
                            ruleIndex = 0
                            while ruleIndex < len(tempRules):
                                changed = False
                                rule = tempRules[ruleIndex]
                                ruleInput = rule[0]
                                ruleOutput = rule[1]
                                
                                while tempOutput != None:
                                    tempOutput = ApplySubstitution((ruleInput, ruleOutput), newOutput)

                                    if tempOutput != None:
                                        newOutput = tempOutput
                                        changed = True
                                
                                if changed:
                                    ruleIndex = -1
                                
                                ruleIndex += 1
                    
                            if CreateInputStringFromTree(ChangeListToTree(newOutput)) != newRule[1]:
                                newRule = (newRule[0], 
                                            CreateInputStringFromTree(ChangeListToTree(newOutput)))
                                
                                if newRule not in nextRules:
                                    nextRules[index] = newRule
                                else:
                                    if index < nextRules.index(newRule):
                                        ruleMarkings[nextRules.index(newRule)] = ruleMarkings[index]
                                        
                                    nextRules.pop(index)
                                    ruleMarkings.pop(index)
                                    
                                    index -= 1
                        
                        index += 1
                    
                    if (normalFormTermInput, normalFormTermOutput) not in nextRules:
                        nextRules.append((normalFormTermInput, normalFormTermOutput))
                        ruleMarkings.append(False)
                    
                    nextIdentities = currIdentities.copy()
                    nextIdentities.remove(identity)
                    index = 0
                    while index < len(currRules):
                        oldIdentity = currRules[index]
                        newIdentity = currRules[index]
                        if newIdentity == identity:
                            index += 1
                            continue
                        elif newIdentity[1] == identity[0] and newIdentity[0] == identity[1]:
                            index += 1
                            continue

                        newInput = ChangeTreeToList(CreateTree(newIdentity[0]))
                        tempInput = ChangeTreeToList(CreateTree(newIdentity[0]))
                        
                        tempInput = ApplySubstitution((normalFormTermInput, normalFormTermOutput), newInput)

                        if tempInput != None:
                            newInput = tempInput
                        
                        if CreateInputStringFromTree(ChangeListToTree(newInput)) != newIdentity[0]:
                            newIdentity = (CreateInputStringFromTree(ChangeListToTree(newInput)), 
                                            newIdentity[1])
                        
                            if newIdentity not in nextIdentities:
                                nextIdentities.append(newIdentity)
                                ruleMarkings.pop(nextRules.index(oldIdentity))
                                nextRules.remove(oldIdentity)
                        
                        index += 1
                        
                    i += 1
                    currRules = nextRules.copy()
                    currIdentities = nextIdentities.copy()

        if False in ruleMarkings:
            nextRules = currRules.copy()
            
            for index in range(len(ruleMarkings)):
                if ruleMarkings[index] == False:
                    ruleMarkings[index] = True
                    break
            
            rulesToGenerateCritPairsWith = []
            combosToGenerateCritPairsWith = []
            for index in range(len(ruleMarkings)):
                if ruleMarkings[index] == True:
                    rulesToGenerateCritPairsWith.append(nextRules[index])
            
            combosToGenerateCritPairsWith.append((len(rulesToGenerateCritPairsWith) - 1, len(rulesToGenerateCritPairsWith) - 1))
            for i in range(len(rulesToGenerateCritPairsWith)):
                for j in range(len(rulesToGenerateCritPairsWith)):
                    if i != j:
                        combosToGenerateCritPairsWith.append((i, j))
            
            # print(f"+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\nGenerating all critical pairs with rules {rulesToGenerateCritPairsWith}")
            
            critPairs = GenerateAllCriticalPairs(rulesToGenerateCritPairsWith, combosToGenerateCritPairsWith)
            
            nextIdentities = []
            for critPair in critPairs:
                str1 = CreateInputStringFromTree(ChangeListToTree(critPair[0]))
                str2 = CreateInputStringFromTree(ChangeListToTree(critPair[1]))
                
                newCritPair = ()
                if len(str1) > len(str2):
                    newCritPair = (critPair[0], critPair[1])
                else:
                    newCritPair = (critPair[1], critPair[0])
                
                newCritPair = RenameVariablesInCritPair(newCritPair[0], newCritPair[1])
                # newCritPair = (critPair[0], critPair[1])
                if newCritPair[0] != newCritPair[1]:
                    str1 = CreateInputStringFromTree(ChangeListToTree(newCritPair[0]))
                    str2 = CreateInputStringFromTree(ChangeListToTree(newCritPair[1]))
                    
                    if (str1, str2) not in nextIdentities and (str2, str1) not in nextIdentities:
                        found = False
                        for rule in nextRules:
                            if (str1, str2) == rule or (str2, str1) == rule:
                                found = True
                                break
                        
                        if not found:
                            # print(f"Added {(str1, str2)} to the set of identities!")
                            with open("out.txt", "a") as f:
                                f.write(f"Added critical pair {(str1, str2)} to the set of identities.\n")
                            nextIdentities.append((str1, str2))
            
            i += 1
            currRules = nextRules.copy()
            currIdentities = nextIdentities.copy()
        
        times += 1
    
    print(f"Succeeded with rules {currRules}.")
    return (True, currRules)
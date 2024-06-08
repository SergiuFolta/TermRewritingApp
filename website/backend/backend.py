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
    
    curr_node = head
    for i in range(0, len(indeces) - 1):
        index = int(indeces[i]) - 1
        if curr_node.next != None:
            curr_node = curr_node.next[index]
        else:
            flash(f"ERROR: Cannot replace subterm at index {index + 1}! The position {position} doesn't exist.", category="error")
            return []
    
    curr_node.next[(int(indeces[-1]) - 1)] = ChangeListToTree(replacement_term)
    
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
    precedences = LoadPrecedences()
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
            if LexicographicPathOrdering(term1, subterm) == False:
                found = True
                break
        
        if not found:
            return 1
            
    # print("In LPO2c")
    # LPO2c)
    if precedences[term1[0]] == precedences[term2[0]]:
        for subterm in subterms2:
            if LexicographicPathOrdering(term1, subterm) == False:
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


def ReplaceCoincidingVariables(vars1: set, vars2: set, term: List, rule: Tuple[str, str]) -> Tuple[List, Tuple[str, str]]:
    nonuniqueVars = vars1.intersection(vars2)
    
    varRules = {}
        
    variables = LoadVariables()
    flatTerm = FlattenList(term)

    for var in nonuniqueVars:
        newVarName = var + "'"
        while newVarName in flatTerm:
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
    
    print(f"Term1 after applying all rules: {term1}")

    critPair1Res = [ApplySubstitutionRecursive(rule1, term1), ApplySubstitution(rule1, term1)]
    critPair2Res = [ApplySubstitutionRecursive(rule2, subterm1), ApplySubstitution(rule2, subterm1)]
    
    # print(f"CritPair1Res = {critPair1Res}")
    # print(f"CritPair2Res = {critPair2Res}")
    
    critPair1Res = [pair for pair in critPair1Res if pair != None]
    critPair2Res = [pair for pair in critPair2Res if pair != None]
    
    if len(critPair1Res) == 0 or len(critPair2Res) == 0:
        return (None, None)
    
    critPair1 = critPair1Res[-1]
    critPair2 = critPair2Res[-1]
    # apply mgu on the first result
    for lhs in rules.keys():
        for rhs in rules[lhs]:
            result = ApplySubstitutionRecursive((lhs, rhs), critPair1)
            if result != None:
                critPair1 = result
            
    # apply mgu on the second result
    for lhs in rules.keys():
        for rhs in rules[lhs]:
            result = ApplySubstitutionRecursive((lhs, rhs), critPair2)
            if result != None:
                critPair2 = result
    
    # replace the subterm at position {position} in {term1} with {critPair2}
    critPair2 = ReplaceSubtermAtPosition(term1, critPair2, position)
    
    # print(f"Critical pair 1: {critPair1}") # f(y', z') ->               ["f", ["y'", "z'"]]
    # print(f"Critical pair 2: {critPair2}") # f(y', f(f(y', z'), z)) ->  ["f", ["y'", "f", ["f", ["y'", "z'"], "z"]]]

    return (critPair1, critPair2)


def GenerateAllCriticalPairs(rules: Dict[str, List]) -> List[Tuple[List, List]]:
    rules = list(rules)
    availableNums = [(num + 1) for num in range(len(rules))]
    combinations = set([])
    for i in range(len(availableNums)):
        for j in range(i + 1, len(availableNums)):
            combinations.add((i, j))
    
    critPairs = []
    for combination in combinations:
        term1 = ChangeTreeToList(CreateTree(rules[combination[0]][0])) # left hand side of rule
        term2 = ChangeTreeToList(CreateTree(rules[combination[1]][0])) # right hand side of rule
        
        # replace all coinciding variables in term2 and reflect changes in rule2 with newRule
        term2, newRule = ReplaceCoincidingVariables(set(GetUniqueVariables(term1)), set(GetUniqueVariables(term2)), term2, rules[combination[1]])
        
        positions = GetAllFunctionPositions(term1)
        
        for position in positions:
            # if TermIsVariable(ChangeTreeToList(CreateTree(rules[combination[0]][1]))) and position == "":
            #     continue
        
            print(f"----------------------------------------------------------------------------------------\n \
                Attempting to find critical pair for:\n \
                Term 1: {term1}\n \
                Term 2: {term2}\n \
                Rule 1: {rules[combination[0]]}\n \
                Rule 2: {newRule}\n \
                Position: {position}")
            
            if GetSubtermAtPosition(term1, position)[0] != term2[0]:
                print(f"Functions have different number of arguments!")
                continue
            
            critPair = GetCriticalPair(
                term1,
                term2,
                rules[combination[0]],
                newRule,
                position
            )
        
            if critPair != (None, None) and critPair[0] != critPair[1]:
                print(f"Found critical pair {critPair}!")
                critPairs.append(critPair)
    
    return critPairs


def RenameVariablesInCritPair(term1: List, term2: List) -> Tuple[List, List]:
    variableOrder = ["x", "y", "z", "w", "a"]
    vars1 = GetUniqueVariables(term1)
    vars2 = GetUniqueVariables(term2)
    maxLen = max(len(vars1), len(vars2))
    maxVars = vars1 if maxLen == len(vars1) else vars2
    
    rules = []
    if maxLen > len(variableOrder):
        print(f"Vars1 = {term1}")
        print(f"Vars2 = {term2}")
        print(f"HEY I NEED MORE VARIABLES OVER HERE!!!!11!!!1!!!!!!!!1!1!!")
        return []
    
    for i in range(maxLen):
        rules.append((maxVars[i], variableOrder[i]))
    
    newTerm1 = ChangeTreeToList(ChangeListToTree(term1))
    newTerm2 = ChangeTreeToList(ChangeListToTree(term2))
    
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


def DetermineCompleteness(identities: set, times: int = 1000) -> bool:
    prevRules = set([])
    currRules = set([])
    identityList = list(identities)
    
    i = 0
    while i < len(identityList):
        identity = identityList[i] # take the current identity
        term1 = ChangeTreeToList(CreateTree(identity[0])) # take left hand side of identity (s)
        term2 = ChangeTreeToList(CreateTree(identity[1])) # take right hand side of identity (t)
        
        if term1 == term2: # if s == t
            identities.discard(identity)
        elif LexicographicPathOrdering(term1, term2) == 1: # if s > t
            identities.discard(identity)
            currRules.add((CreateInputStringFromTree(ChangeListToTree(term1)), CreateInputStringFromTree(ChangeListToTree(term2))))
        elif LexicographicPathOrdering(term2, term1) == 1: # if t > s
            identities.discard(identity)
            currRules.add((CreateInputStringFromTree(ChangeListToTree(term2)), CreateInputStringFromTree(ChangeListToTree(term1))))
        else:
            return False
        
        i += 1
    
    print(f"Rules before critical pairs: {currRules}")
    
    while currRules != prevRules:
        prevRules = currRules.copy()
        
        print(f"Prev Rules = {prevRules}")
        # compute all critical pairs under our rule set prevRules
        critPairs = GenerateAllCriticalPairs(prevRules)
        print(f"Crit Pairs = {critPairs}")
        
        # reduce all critical pairs to normal form under our rule set prevRules
        for critPair in critPairs:
            oldPair = RenameVariablesInCritPair(critPair[0], critPair[1])
            newPair = RenameVariablesInCritPair(critPair[0], critPair[1])
            
            for rule in prevRules:
                term1 = ApplySubstitution(rule, newPair[0])
                term2 = ApplySubstitution(rule, newPair[1])
                
                if term1 == None:
                    term1 = newPair[0]
                else:
                    print(f"Applied rule {rule} on {newPair[0]} and obtained {term1}")
                
                if term2 == None:
                    term2 = newPair[1]
                
                newPair = (term1, term2)
            
            print(f"New pair: {newPair}\n \
                        Old pair: {oldPair}")
            
            if LexicographicPathOrdering(newPair[0], newPair[1]) == 1: # if critPair1 > critPair2, then currRules += (critPair1, critPair2)
                currRules.add((CreateInputStringFromTree(ChangeListToTree(newPair[0])),
                                CreateInputStringFromTree(ChangeListToTree(newPair[1])))) 
            elif LexicographicPathOrdering(newPair[1], newPair[0]) == 1: # if critPair2 > critPair1, then currRules += (critPair2, critPair1)
                currRules.add((CreateInputStringFromTree(ChangeListToTree(newPair[1])),
                                CreateInputStringFromTree(ChangeListToTree(newPair[0])))) 
            elif newPair[0] != newPair[1]:
                print(f"Failed at pair with rules {prevRules}:\noldPair: {oldPair}\nnewPair: {newPair}")
                return False # if there is one critical pair in normal form which cannot be ordered, fail
        
        times -= 1
        
        if times == 0:
            print(f"This has been going on for too long.")
            return False

    print(f"Rules after critical pairs: {currRules}")

    return True

from flask import session
from .database import *

def ModifyPrecedence() -> None:
    functions = LoadFunctions()
    functions = dict(sorted(functions.items(), key=lambda item: item[1]))
    variables = LoadVariables()
    current_precedence = 0

    precedences = {}
    
    for func in functions.keys():
        precedences[func] = current_precedence
        current_precedence += 1
    
    for var in variables:
        precedences[var] = current_precedence
        current_precedence += 1

    SavePrecedences(precedences)

import os
from flask import Blueprint, render_template, request, session, current_app as app
from website.backend.backend import *

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    input_string = session["input_string"] if "input_string" in session else ""
    tree = ""
    
    if request.method == 'POST':
        input_string = request.form.get('term')
        session["input_string"] = input_string
        
        if request.form.get('detect'):
            LoadLanguage(input_string)
            
        if request.form.get('create'):
            head = CreateTree(input_string)
            tree = ChangeTreeToList(head)
            
    
    functions = session["functions"] if "functions" in session else {}
    variables = session["variables"] if "variables" in session else set([])
    return render_template("home.html", input_string = input_string, functions = functions, variables = variables, tree = tree)

@views.route('/functions', methods=['GET', 'POST'])
def functions():
    functions = session["functions"] if "functions" in session else {}
    
    if request.method == 'POST':
        if request.form.get('addnew'):
            function_name = request.form.get('functionnew')
            function_arity = int(request.form.get('aritynew'))
            AddFunction(function_name, function_arity)
            
            functions = dict(sorted(session["functions"].items()))
            
        for i,f in enumerate(functions.keys()):
            if request.form.get('modify' + str(i + 1)):
                function_name = request.form.get('function' + str(i + 1))
                function_arity = int(request.form.get('arity' + str(i + 1)))
                ModifyFunction(f, function_name, function_arity)  
                break
            
            if  request.form.get('delete' + str(i + 1)):
                DeleteFunction(f)
                break
    
    return render_template("functions.html", functions = functions)

@views.route('/variables', methods=['GET', 'POST'])
def variables():
    variables = set(session["variables"]) if "variables" in session else set([])
    
    if request.method == 'POST':
        if request.form.get('addnew'):
            var_name = request.form.get('varnew')
            AddVariable(var_name)
            
        for i,v in enumerate(variables):
            if request.form.get('modify' + str(i + 1)):
                var_name = request.form.get('var' + str(i + 1))
                ModifyVariable(v, var_name)
                break
            
            if  request.form.get('delete' + str(i + 1)):
                DeleteVariable(v)
                break
            
        variables = set(session["variables"])
    
    return render_template("variables.html", variables = variables)

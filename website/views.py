import os
from flask import Blueprint, render_template, redirect, url_for, request, session, current_app as app
from website.backend.backend import *

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    functions = LoadFunctions()
    variables = LoadVariables()
    term_name = session["term_name"] if "term_name" in session else ""
    term_string = session["term_string"] if "term_string" in session else ""
    term_dictionary = session["terms"] if "terms" in session else {}
    terms = term_dictionary.keys()
    tree = ""
    
    if request.method == 'POST':  
        if request.form.get('functions'):
            return redirect(url_for('views.functions', functions = functions))
        
        if request.form.get('variables'):
            return redirect(url_for('views.variables', variables = variables))
        
        if request.form.get('terms'):
            return redirect(url_for('views.terms', functions = functions, variables = variables, terms = terms, tree = tree))
        
        if request.form.get('create'):
            return redirect(url_for('views.createterm', term_name = term_name, term_string = term_string, functions = functions, variables = variables, terms = terms))
            
    return render_template("home.html")

@views.route('/functions', methods=['GET', 'POST'])
def functions():
    functions = LoadFunctions()
    
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
            
            if request.form.get('delete' + str(i + 1)):
                DeleteFunction(f)
                break
        
        if request.form.get('home'):
            return redirect(url_for('views.home'))
    
    return render_template("functions.html", functions = functions)

@views.route('/variables', methods=['GET', 'POST'])
def variables():
    variables = LoadVariables()
    
    if request.method == 'POST':
        if request.form.get('home'):
            return redirect(url_for('views.home'))
        
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
            
        SaveVariables(variables)
    
    return render_template("variables.html", variables = variables)

@views.route('/terms', methods=['GET', 'POST'])
def terms():
    functions = LoadFunctions()
    variables = LoadVariables()
    term_dictionary = session["terms"] if "terms" in session else {}
    terms = term_dictionary.keys()
    tree = ""
    
    if request.method == 'POST':    
        if request.form.get('display'):
            term_name = request.form.get('term')
            tree = LoadTerm(term_name)
            if tree is not None:
                tree = tree[1]
        
        if request.form.get('home'):
            return redirect(url_for('views.home'))
            
    return render_template("terms.html", functions = functions, variables = variables, terms = terms, tree = tree)

@views.route('/createterm', methods=['GET', 'POST'])
def createterm():
    term_name = session["term_name"] if "term_name" in session else ""
    term_string = session["term_string"] if "term_string" in session else ""
    
    if request.method == 'POST':
        term_name = request.form.get('name')
        term_string = request.form.get('string')
        session["term_name"] = term_name
        session["term_string"] = term_string
        
        if request.form.get('detect'):
            LoadLanguage(term_string)
            
        if request.form.get('save'):
            head = CreateTree(term_string)
            tree = ChangeTreeToList(head)
            SaveTerm(tree, term_string, term_name)
            
        if request.form.get('home'):
            return redirect(url_for('views.home'))
    
    functions = LoadFunctions()
    variables = LoadVariables()
    term_dictionary = session["terms"] if "terms" in session else {}
    terms = term_dictionary.keys()
    return render_template("createterm.html", term_name = term_name, term_string = term_string, functions = functions, variables = variables, terms = terms)

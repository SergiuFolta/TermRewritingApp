import os
from flask import Blueprint, render_template, redirect, url_for, request, session, current_app as app
from website.backend.backend import *

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    functions = LoadFunctions()
    variables = LoadVariables()
    substitutions = LoadSubstitutions()
    term_name = session["term_name"] if "term_name" in session else ""
    term_string = session["term_string"] if "term_string" in session else ""
    term_dictionary = session["terms"] if "terms" in session else {}
    terms = term_dictionary.keys()
    tree = ""
    term_selected = ""
    tree1 = ""
    term_selected1 = ""
    tree2 = ""
    term_selected2 = ""
    tree3 = ""
    
    if request.method == 'POST':  
        if request.form.get('functions'):
            return redirect(url_for('views.functions', functions = functions))
        
        if request.form.get('variables'):
            return redirect(url_for('views.variables', variables = variables))
        
        if request.form.get('terms'):
            return redirect(url_for('views.terms', functions = functions, variables = variables, terms = terms, term_selected = term_selected, tree = tree))
        
        if request.form.get('create'):
            return redirect(url_for('views.createterm', term_name = term_name, term_string = term_string, functions = functions, variables = variables, terms = terms))
        
        if request.form.get('replace'):
            return redirect(url_for("views.replace", terms = terms, term_selected1 = term_selected1, term_selected2 = term_selected2, tree1 = tree1, tree2 = tree2, tree3 = tree3))
        
        if request.form.get('substitutions'):
            return redirect(url_for('views.substitutions', substitutions = substitutions))
        
        if request.form.get('unification'):
            return redirect(url_for('views.unification', substitutions = substitutions))
            
    return render_template("home.html")

@views.route('/functions', methods=['GET', 'POST'])
def functions():
    functions = LoadFunctions()
    
    if request.method == 'POST':
        if request.form.get('home'):
            return redirect(url_for('views.home'))
        
        if request.form.get('addnew'):
            function_name = request.form.get('functionnew')
            function_arity = int(request.form.get('aritynew'))
            AddFunction(function_name, function_arity)
            
            functions = dict(sorted(LoadFunctions().items()))
            
        for i,f in enumerate(functions.keys()):
            if request.form.get('modify' + str(i + 1)):
                function_name = request.form.get('function' + str(i + 1))
                function_arity = int(request.form.get('arity' + str(i + 1)))
                ModifyFunction(f, function_name, function_arity)  
                functions = dict(sorted(LoadFunctions().items()))
                break
            
            if request.form.get('delete' + str(i + 1)):
                DeleteFunction(f)
                break
    
    return render_template("functions.html", functions = functions)

@views.route('/variables', methods=['GET', 'POST'])
def variables():
    variables = LoadVariables().keys()
    
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
            
        variables = LoadVariables().keys()
    
    return render_template("variables.html", variables = variables)

@views.route('/terms', methods=['GET', 'POST'])
def terms():
    functions = LoadFunctions()
    variables = LoadVariables().keys()
    term_dictionary = session["terms"] if "terms" in session else {}
    terms = term_dictionary.keys()
    tree = ""
    term_selected = ""
    
    if request.method == 'POST':    
        if request.form.get('home'):
            return redirect(url_for('views.home'))
        
        if request.form.get('display'):
            term_name = request.form.get('term')
            term_selected = term_name
            tree = LoadTerm(term_name)
            if tree is not None:
                tree = tree[1]
                
        if request.form.get('ground'):
            term_name = request.form.get('term')
            term_selected = term_name
            tree = LoadTerm(term_name)
            if tree is not None:
                tree = tree[1]
            if tree and IsTermGround(tree):
                flash("The term \'" + term_name + "\' is ground!")
            elif tree:
                flash("The term \'" + term_name + "\' is not ground!", category="error")
            tree = ""
            
    return render_template("terms.html", functions = functions, variables = variables, terms = terms, term_selected = term_selected, tree = tree)

@views.route('/createterm', methods=['GET', 'POST'])
def createterm():
    term_name = session["term_name"] if "term_name" in session else ""
    term_string = session["term_string"] if "term_string" in session else ""
    
    if request.method == 'POST':
        if request.form.get('home'):
            return redirect(url_for('views.home'))
        
        term_name = request.form.get('name')
        term_string = request.form.get('string')
        session["term_name"] = term_name
        session["term_string"] = term_string
        
        if request.form.get('detect'):
            terms = LoadAllTerms()
            
            if len(terms) >= 2:
                term_1 = terms["term1"][1]
                term_2 = terms["term2"][1]
                print(LexicographicPathOrdering(term_1, term_2))
                print(LoadPrecedences())
            
        if request.form.get('save'):
            head = CreateTree(term_string)
            tree = ChangeTreeToList(head)
            SaveTerm(tree, term_string, term_name)
    
    functions = LoadFunctions()
    variables = LoadVariables().keys()
    term_dictionary = session["terms"] if "terms" in session else {}
    terms = term_dictionary.keys()
    return render_template("createterm.html", term_name = term_name, term_string = term_string, functions = functions, variables = variables, terms = terms)

@views.route('/replace', methods=['GET', 'POST'])
def replace():
    term_dictionary = session["terms"] if "terms" in session else {}
    terms = term_dictionary.keys()
    tree1 = ""
    term_selected1 = ""
    tree2 = ""
    term_selected2 = ""
    tree3 = ""
    term_string = ""
    term_name = ""
    
    if request.method == 'POST': 
        if request.form.get('home'):
            return redirect(url_for('views.home'))
        
        if request.form.get('display'):
            term_name1 = request.form.get('term1')
            term_selected1 = term_name1
            tree1 = LoadTerm(term_name1)
            
            if tree1 is not None:
                tree1 = tree1[1]
            
            term_name2 = request.form.get('term2')
            term_selected2 = term_name2
            tree2 = LoadTerm(term_name2)
            if tree2 is not None:
                tree2 = tree2[1]
                
        if request.form.get('replace'):
            term_name1 = request.form.get('term1')
            term_selected1 = term_name1
            
            term_name2 = request.form.get('term2')
            term_selected2 = term_name2
            
            replace_index = request.form.get('replace_index')
            
            #Create the new term
            if replace_index == None: # if no radio button has been selected
                flash("ERROR: You need to select a subterm from the left term!", category="error")
            else:
                replace_index = int(replace_index)
                term1 = LoadTerm(term_selected1)[1]
                term2 = LoadTerm(term_selected2)[1]
                replace_position = GetPositionFromListIndex(term1, replace_index)
                
                tree3 = ReplaceSubtermAtPosition(term1, term2, replace_position)
                
                term_string = CreateInputStringFromTree(ChangeListToTree(tree3))
        
        if request.form.get('save'):
            term_name = request.form.get('name')
            term_string = request.form.get('string')
            tree3 = CreateTree(term_string)
            tree3 = ChangeTreeToList(tree3)
            SaveTerm(tree3, term_string, term_name)
            term_dictionary = session["terms"] if "terms" in session else {}
            
            
    return render_template("replace.html", terms = terms, term_selected1 = term_selected1, term_selected2 = term_selected2, tree1 = tree1, tree2 = tree2, tree3 = tree3, term_string = term_string, term_name = term_name)

@views.route('/substitutions', methods=['GET', 'POST'])
def substitutions():
    substitutions = LoadSubstitutions()
    
    if request.method == 'POST':
        if request.form.get('home'):
            return redirect(url_for('views.home'))
        
        if request.form.get('addnew'):
            sub_in = request.form.get('subinnew')
            sub_out = request.form.get('suboutnew')
            AddSubstitution(sub_in, sub_out)
            
            substitutions = dict(sorted(LoadSubstitutions().items()))
        
        i = 0 
        k = 0   
        for sub in substitutions.keys():
            for subs in substitutions[sub]:  
                if request.form.get('modify' + str(i + 1)):
                    sub_in = request.form.get('subin' + str(i + 1))
                    sub_out = request.form.get('subout' + str(i + 1))
                    ModifySubstitution(sub, subs, sub_in, sub_out)
                    substitutions = dict(sorted(LoadSubstitutions().items()))
                    k = 1
                    break
                
                if  request.form.get('delete' + str(i + 1)):
                    print(i)
                    DeleteSubstitution(sub, subs)
                    k = 1
                    break
                
                i = i + 1
                
            if k:
                break
    
    return render_template("substitutions.html", substitutions = substitutions)

@views.route('/unification', methods=['GET', 'POST'])
def unification():
    substitutions = LoadSubstitutions()
    old_substitutions = {}
    
    if request.method == 'POST':
        if request.form.get('home'):
            return redirect(url_for('views.home'))
        
        if request.form.get('unify'):
            old_substitutions = substitutions
            
            #Unify
    
    return render_template("unification.html", substitutions = substitutions, old_substitutions = old_substitutions)

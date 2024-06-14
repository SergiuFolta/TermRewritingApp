import os
from flask import Blueprint, render_template, redirect, url_for, request, session, current_app as app
from website.backend.backend import *

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    functions = {"f": 2, "e": 0, "i": 1}
    variables = set(["x", "y", "z"])
    substitutions = {"f(f(x, y), z)": ["f(x, f(y, z))"], "f(e, x)": ["x"], "f(i(x), x)": ["e"]}
    # substitutions = {"f(f(x, y), z)": ["f(x, f(y, z))"], "f(e, x)": ["x"], "f(x, i(x))": ["e"]}
    SaveFunctions(functions)
    SaveVariables(variables)
    SaveSubstitutions(substitutions)
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
        
        if request.form.get('lpo'):
            return redirect(url_for('views.lpo', substitutions = substitutions))
        
        if request.form.get('critpair'):
            return redirect(url_for('views.critpair', substitutions = [], input_selected1 = "", input_selected2 = "", tree1 = "", tree2 = "", critPairRep = ""))
        
        if request.form.get('complete'):
            return redirect(url_for('views.complete', substitutions = [], rules = []))
        
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
            
        variables = LoadVariables()
    
    return render_template("variables.html", variables = variables)

@views.route('/terms', methods=['GET', 'POST'])
def terms():
    functions = LoadFunctions()
    variables = LoadVariables()
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
            
            # if len(terms) >= 2:
            #     term_1 = terms["term1"][1]
            #     term_2 = terms["term2"][1]
            #     print(LexicographicPathOrdering(term_1, term_2))
            #     print(LoadPrecedences())
            print(LexicographicPathOrdering(["i", ["f", ["x", "y"]]], ["f", ["i", ["y"], "i", ["x"]]]))
            
            # print(ApplySubstitution(("f(f(x, y), z)", "f(x, f(y, z))"), ["f", ["f", ["x", "y"], "i", ["f", ["x", "y"]]]]))
            
            # print(ApplySubstitution(("f(x', i(x'))", "e"), ["f", ["f", ["x", "y"], "i", ["f", ["x", "y"]]]]))
            
            # print(Unification({
            #     "x": ["f(a)"],
            #     "g(x, x)": ["g(x, y)"]
            # }))
            
            # print(RuleEliminateSubstitutions({
            #     "x": ["i(a)", "x"],
            #     "g(x, y)": ["i(x)", "g(x, a)", "g(x, y)"],
            #     "i(x)": ["i(y)", "y"],
            #     "y": ["g(x, a)", "y"]
            # }))
            
            # print(GetAllFunctionPositions(["f", ["f", ["x", "y"], "i", ["f", ["x", "i", ["y"]]]]]))
            
            # print(GetUniqueVariables(["f", ["f", ["x", "y"], "i", ["f", ["x", "i", ["y"]]]]]))
            
            # print(ReplaceCoincidingVariables(set(["x", "y"]), set(["x", "y", "a"]), ["f", ["f", ["x", "y"], "i", ["f", ["a", "i", ["y"]]]]]))
            
            # print(GetSubtermAtPosition(["f", ["f", ["x", "z"], "f", ["z", "i", ["y"]]]], "2_2_1"))
            
            # print(GetCriticalPair(["f", ["f", ["x", "y"], "z"]], 
            #                         ["f", ["x'", "i", ["x'"]]],
            #                         ("f(f(x, y), z)", "f(x, f(y, z))"),
            #                         ("f(x, i(x))", "e"),
            #                         ""))
            
            # print(GetCriticalPair(["f", ["f", ["x", "y"], "z"]], 
            #                         ["f", ["i", ["x'"], "x'"]],
            #                         ("f(f(x, y), z)", "f(x, f(y, z))"),
            #                         ("f(i(x), x)", "e"),
            #                         "1"))
            
            # term1 = ["f", ["f", ["x", "y"], "f", ["y", "z"]]]
            # print(f"After replacement: {ReplaceCoincidingVariables(GetUniqueVariables(term1), GetUniqueVariables(term1), term1)}")
            
            # print(GetCriticalPair(term1, 
            #                         ReplaceCoincidingVariables(GetUniqueVariables(term1), GetUniqueVariables(term1), term1),
            #                         ("f(f(x, y), f(y, z))", "y"),
            #                         ("f(f(x', y'), f(y', z'))", "y'"),
            #                         "1"))
            
            # print(DetermineCompleteness(set([("f(f(x, y), f(y, z))", "y")]))) # true, yeeeey
            
            # print(DetermineCompleteness(set([("g(x, f(y, z))", "f(g(x, y), g(x, z))"), ("g(f(u, v), w)", "f(g(u, w), g(v, w))")])))
            # f = +
            # g = *
            
            # print(ApplySubstitution(("f(x', f(f(y', w), w))", "f(x', f(y', f(w, w)))"), ['f', ['f', ['x', 'y'], 'z']]))
            
            # print(DetermineCompletenessHuet([
            #     ("f(f(x, y), z)", "f(x, f(y, z))"),
            #     ("f(e, x)", "x"),
            #     ("f(i(x), x)", "e")
            # ]))
            
            # print(GetCriticalPair(['f', ['f', ['x', 'y'], 'z']],
            #                         ['f', ['i', ["x'"], "x'"]],
            #                         ('f(f(x, y), z)', 'f(x, f(y, z))'),
            #                         ("f(i(x'), x')", 'e'),
            #                         "1"))
            
            # Example usage:
            string1 = "f(f(x,y),z)"
            string2 = "f(x,f(y,z))"
            rules = create_regex_substitution(string1, string2)
            print(rules)

            # Test the function
            input_string = 'f(f(x\',f(y\',z\')),z)'
            print(re.search(rules[0][0], input_string))
            transformed_string = transform_string(input_string, rules)
            print(transformed_string)
            
            # rule1 = "f(x', f(y', f(z', f(z, z))))"
            # rule2 = "f(x', f(y', f(z', z)))"
            # term1 = ChangeTreeToList(CreateTree(rule1))
            # term2 = ChangeTreeToList(CreateTree(rule2))
            # position = ""
            
            # firstOrdering = LexicographicPathOrdering(term1, term2)
            # secondOrdering = LexicographicPathOrdering(term2, term1)
            # if firstOrdering == 1:
            #     flash(f"{term1} > {term2}")
            # elif secondOrdering == 1:
            #     flash(f"{term2} > {term1}")
            # else:
            #     flash(f"Cannot be ordered!")
            
            # if firstOrdering == 1 or secondOrdering == 1:
            #     print(GetCriticalPair(term1,
            #                             term2,
            #                             rule1,
            #                             rule2,
            #                             position))
            
        if request.form.get('save'):
            head = CreateTree(term_string)
            tree = ChangeTreeToList(head)
            SaveTerm(tree, term_string, term_name)
    
    functions = LoadFunctions()
    variables = LoadVariables()
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
            print(term_name1)
                
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
            
            substitutions = Unification(substitutions)
    
    return render_template("unification.html", substitutions = substitutions, old_substitutions = old_substitutions)


@views.route('/lpo', methods=['GET', 'POST'])
def lpo():
    substitutions = LoadSubstitutions()
    old_substitutions = {}
    
    if request.method == 'POST':
        if request.form.get('home'):
            return redirect(url_for('views.home'))
        
        if request.form.get('lpo'):
            old_substitutions = substitutions
            new_substitutions = {}
            
            for input in substitutions:
                for output in substitutions[input]:
                    substitution = (input, output)
                    term1 = ChangeTreeToList(CreateTree(substitution[0]))
                    term2 = ChangeTreeToList(CreateTree(substitution[1]))
                    
                    if LexicographicPathOrdering(term1, term2) == 1:
                        str1 = CreateInputStringFromTree(ChangeListToTree(term1))
                        str2 = CreateInputStringFromTree(ChangeListToTree(term2))
                        
                        if str1 in new_substitutions.keys():
                            new_substitutions[str1].append(str2)
                        else:
                            new_substitutions[str1] = [str2]
                    elif LexicographicPathOrdering(term2, term1) == 1:
                        str1 = CreateInputStringFromTree(ChangeListToTree(term1))
                        str2 = CreateInputStringFromTree(ChangeListToTree(term2))
                        
                        if str2 in new_substitutions.keys():
                            new_substitutions[str2].append(str1)
                        else:
                            new_substitutions[str2] = [str1]
                
            substitutions = new_substitutions
    
    return render_template("lpo.html", substitutions = substitutions, old_substitutions = old_substitutions)


@views.route('/critpair', methods=['GET', 'POST'])
def critpair():
    substitutions = LoadSubstitutions()
    substitutionsStr = []
    for input in substitutions:
        for output in substitutions[input]:
            substitutionsStr.append(f"{input} -> {output}")
    
    tree1 = ""
    rule1 = ""
    tree2 = ""
    rule2 = ""
    critPairRep = ""
    
    if request.method == 'POST': 
        if request.form.get('home'):
            return redirect(url_for('views.home'))
        
        if request.form.get('display'):
            rule1 = request.form.get('rule1')
            input_selected1 = rule1[:(rule1.find("-") - 1)]
            tree1 = ChangeTreeToList(CreateTree(input_selected1))
            
            rule2 = request.form.get('rule2')
            input_selected2 = rule2[:(rule2.find("-") - 1)]
            tree2 = ChangeTreeToList(CreateTree(input_selected2))
                
        if request.form.get('compute'):
            rule1 = request.form.get('rule1')
            input_selected1 = rule1[:(rule1.find("-") - 1)]
            
            rule2 = request.form.get('rule2')
            input_selected2 = rule2[:(rule2.find("-") - 1)]
            
            replace_index = request.form.get('replace_index')
            
            #Create the new term
            if replace_index == None: # if no radio button has been selected
                flash("ERROR: You need to select a subterm from the left term!", category="error")
            else:
                replace_index = int(replace_index)
                term1 = ChangeTreeToList(CreateTree(input_selected1))
                term2 = ChangeTreeToList(CreateTree(input_selected2))
                replace_position = GetPositionFromListIndex(term1, replace_index)
                
                output_selected1 = rule1[(rule1.find(">") + 2):]
                output_selected2 = rule2[(rule2.find(">") + 2):]
                
                critPair = GetCriticalPair(term1, 
                                            term2,
                                            (input_selected1, output_selected1),
                                            (input_selected2, output_selected2),
                                            replace_position)
                
                print(critPair)
                
                if critPair != (None, None):
                    critPairRep = f"{CreateInputStringFromTree(ChangeListToTree(critPair[0]))} > {CreateInputStringFromTree(ChangeListToTree(critPair[1]))}"
                else:
                    flash("ERROR: Could not find a critical pair for this configuration!", category="error")
                
    return render_template("critpair.html", substitutions = substitutionsStr, input_selected1 = rule1, input_selected2 = rule2, tree1 = tree1, tree2 = tree2, critPairRep = critPairRep)


@views.route('/complete', methods=['GET', 'POST'])
def complete():
    substitutions = LoadSubstitutions()
    rules = []
    
    if request.method == 'POST':
        if request.form.get('home'):
            return redirect(url_for('views.home'))
        
        if request.form.get('complete'):
            new_substitutions = []
            
            for input in substitutions:
                for output in substitutions[input]:
                    substitution = (input, output)
                    new_substitutions.append(substitution)
            
            with open("out.txt", "w+") as f:
                f.write(f"The input is: {new_substitutions}.\n")
            res = DetermineCompletenessHuet(new_substitutions, 25)
            
            rules = res[1]
            with open("out.txt", "a") as f:
                f.write(f"The output is: {rules}.")
                
            if res[0] == True:
                flash(f"Found a convergent Term Rewriting System!")
            else:
                flash(f"ERROR: Couldn't find a convergent Term Rewriting System!", category="error")
    
    return render_template("complete.html", substitutions = substitutions, rules = rules)


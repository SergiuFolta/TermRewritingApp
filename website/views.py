import os
from flask import Blueprint, render_template, request, session, current_app as app
from website.backend import LoadLanguage, CreateTree, PrintTreeNode

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    input_string = session["input_string"] if "input_string" in session else ""
    tree = ""
    
    if request.method == 'POST':
        input_string = request.form.get('term')
        
        if request.form.get('detect'):
            LoadLanguage(input_string)
            
        if request.form.get('create'):
            head = CreateTree(input_string)
            tree = PrintTreeNode(head)
            
    
    functions = session["functions"] if "functions" in session else {}
    variables = session["variables"] if "variables" in session else set([])
    return render_template("home.html", input_string = input_string, functions = functions, variables = variables, tree = tree)
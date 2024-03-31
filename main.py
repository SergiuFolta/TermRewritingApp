from website import create_app
from flask import Flask

if __name__ == '__main__':
    app = Flask("TRApp")
    with app.app_context():
        app = create_app()
        app.run(debug=True)

import os
from flask import Flask
from dotenv import load_dotenv
from src.app.database import init_db
from src.app.routes.auth import auth
from src.app.routes.utilities import utilities
from src.app.routes.groups import groups
from src.app.routes.home import home
from src.app.routes.setup import setup
from src.app.routes.subscriptions import subscriptions
from src.app.routes.expenses import expenses

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.environ.get("APP_SECRET_KEY")

    with app.app_context():
        init_db()
    
    app.register_blueprint(home)
    app.register_blueprint(auth)
    app.register_blueprint(setup)
    app.register_blueprint(utilities)
    app.register_blueprint(groups)
    app.register_blueprint(subscriptions)
    app.register_blueprint(expenses)

    return app

        
    
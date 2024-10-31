from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from models import db, User, Document, Patient
from routes.auth import auth_bp
from routes.documents import documents_bp
from routes.patients import patients_bp
from routes.main import main_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Modify DATABASE_URL to handle SSL requirements
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Remove any existing sslmode parameter
    if '?' in database_url:
        database_url = database_url.split('?')[0]
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url + '?sslmode=require'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(documents_bp)
app.register_blueprint(patients_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)

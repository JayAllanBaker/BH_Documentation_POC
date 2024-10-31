from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from models import db, User, Document, Patient
from routes.auth import auth_bp
from routes.documents import documents_bp
from routes.patients import patients_bp
from routes.main import main_bp
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Configure database with SSL
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Parse the existing URL
    parsed = urlparse(database_url)
    
    # Get existing query parameters
    params = parse_qs(parsed.query) if parsed.query else {}
    
    # Update SSL parameters
    ssl_params = {
        'sslmode': ['require'],  # Changed from verify-ca to require
        'connect_timeout': ['30']
    }
    params.update(ssl_params)
    
    # Create new query string
    query = urlencode(params, doseq=True)
    
    # Reconstruct URL with new query parameters
    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        query,
        parsed.fragment
    ))
    
    app.config['SQLALCHEMY_DATABASE_URI'] = new_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"  # Fallback for development

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

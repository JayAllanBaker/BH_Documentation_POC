from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
import os
import logging
from models import db, User, Document, Patient
from routes.auth import auth_bp
from routes.documents import documents_bp
from routes.patients import patients_bp
from routes.main import main_bp
from routes.conditions import conditions_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Configure database
try:
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Configure SQLAlchemy for PostgreSQL with SSL
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {
                'sslmode': 'verify-ca',
                'sslcert': None,
                'sslkey': None,
                'sslrootcert': '/etc/ssl/certs/ca-certificates.crt'
            },
            'pool_pre_ping': True,
            'pool_size': 5,
            'max_overflow': 2,
            'pool_timeout': 30,
            'pool_recycle': 1800
        }
        logger.info("Using PostgreSQL database with SSL configuration")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
        logger.warning("Using SQLite database (development mode)")
except Exception as e:
    logger.error(f"Error configuring database: {str(e)}")
    raise

# Basic SQLAlchemy configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
try:
    db.init_app(app)
    migrate = Migrate(app, db)
    logger.info("Database initialization successful")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")
    raise

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
app.register_blueprint(conditions_bp)

if __name__ == '__main__':
    with app.app_context():
        try:
            # Test database connection
            db.engine.connect()
            logger.info("Database connection test successful")
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            raise
    app.run(host='0.0.0.0', port=5000)

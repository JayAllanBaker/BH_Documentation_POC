import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configure app
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "dev_key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# Import and register blueprints
from routes.auth import auth_bp
from routes.audio import audio_bp
from routes.documentation import docs_bp

app.register_blueprint(auth_bp)
app.register_blueprint(audio_bp)
app.register_blueprint(docs_bp)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('documentation.list'))
    return redirect(url_for('auth.login'))

with app.app_context():
    import models
    db.drop_all()
    db.create_all()
    
    # Create test user if it doesn't exist
    if models.User.query.filter_by(username='test_provider').first() is None:
        test_user = models.User(
            username='test_provider',
            email='test@example.com'
        )
        test_user.set_password('testpass123')
        db.session.add(test_user)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))
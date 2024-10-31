from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(512), nullable=False)  # Increased from 256 to 512
    role = db.Column(db.String(20), nullable=False, default='user')
    documents = db.relationship('Document', backref='author', lazy=True)

    __table_args__ = (
        db.Index('unique_email_when_not_null', 'email', unique=True, 
                 postgresql_where=(email != None)),
    )

    def set_password(self, password):
        if not password:
            raise ValueError('Password cannot be empty')
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        if not password or not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    audio_file = db.Column(db.String(500))
    transcription = db.Column(db.Text)
    meat_monitoring = db.Column(db.Text)
    meat_assessment = db.Column(db.Text)
    meat_evaluation = db.Column(db.Text)
    meat_treatment = db.Column(db.Text)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # FHIR Identifier
    identifier = db.Column(db.String(50), unique=True)
    # FHIR HumanName
    family_name = db.Column(db.String(100), nullable=False)
    given_name = db.Column(db.String(100), nullable=False)
    # FHIR Administrative Gender
    gender = db.Column(db.String(20))
    # FHIR Date of birth
    birth_date = db.Column(db.Date)
    # FHIR ContactPoint (phone)
    phone = db.Column(db.String(20))
    # FHIR ContactPoint (email)
    email = db.Column(db.String(120))
    # FHIR Address
    address_line = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    # Active status
    active = db.Column(db.Boolean, default=True)
    # Created and updated timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    documents = db.relationship('Document', backref='patient', lazy=True)

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import or_

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    documents = db.relationship('Document', backref='author', lazy=True)

    __table_args__ = (
        db.Index('unique_email_when_not_null', 'email', unique=True, 
                postgresql_where=db.text('email IS NOT NULL')),
    )

    def set_password(self, password):
        if not password:
            raise ValueError('Password cannot be empty')
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not password or not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    before_value = db.Column(db.Text)
    after_value = db.Column(db.Text)
    
    user = db.relationship('User', backref='audit_logs')

    __table_args__ = (
        db.Index('idx_audit_timestamp', 'timestamp'),
        db.Index('idx_audit_action_type', 'action', 'resource_type'),
    )

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

    __table_args__ = (
        db.Index('idx_document_title', 'title'),
        db.Index('idx_document_content', 'content'),
        db.Index('idx_document_patient', 'patient_id'),
    )

class PatientIdentifier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    identifier_type = db.Column(db.String(50), nullable=False)
    identifier_value = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_patient_identifier_type_value', 'identifier_type', 'identifier_value'),
    )

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(50), unique=True)
    family_name = db.Column(db.String(100), nullable=False)
    given_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20))
    birth_date = db.Column(db.Date)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address_line = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    documents = db.relationship('Document', backref='patient', lazy=True)
    identifiers = db.relationship('PatientIdentifier', backref='patient', lazy=True, cascade='all, delete-orphan')
    conditions = db.relationship('Condition', backref='patient', lazy=True, cascade='all, delete-orphan')

    __table_args__ = (
        db.Index('idx_patient_name', 'family_name', 'given_name'),
        db.Index('idx_patient_identifier', 'identifier'),
        db.Index('idx_patient_location', 'city', 'state', 'country'),
    )

    @staticmethod
    def generate_identifier():
        latest_patient = Patient.query.order_by(Patient.id.desc()).first()
        if latest_patient:
            next_id = latest_patient.id + 1
        else:
            next_id = 1
        return f'P{next_id:06d}'

class Condition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(50), unique=True)
    clinical_status = db.Column(db.String(50), nullable=False)
    verification_status = db.Column(db.String(50))
    category = db.Column(db.String(50))
    severity = db.Column(db.String(50))
    code = db.Column(db.String(100))
    code_system = db.Column(db.String(100))
    body_site = db.Column(db.String(100))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    onset_date = db.Column(db.Date)
    onset_string = db.Column(db.String(200))
    abatement_date = db.Column(db.Date)
    abatement_string = db.Column(db.String(200))
    recorded_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_condition_code', 'code'),
        db.Index('idx_condition_status', 'clinical_status'),
        db.Index('idx_condition_patient', 'patient_id'),
    )

    @staticmethod
    def generate_identifier():
        latest_condition = Condition.query.order_by(Condition.id.desc()).first()
        if latest_condition:
            next_id = latest_condition.id + 1
        else:
            next_id = 1
        return f'C{next_id:06d}'

class ICD10Code(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_icd10_code', 'code'),
        db.Index('idx_icd10_description', 'description'),
    )
    
    @staticmethod
    def search_codes(query, limit=10):
        return ICD10Code.query.filter(
            or_(
                ICD10Code.code.ilike(f'{query}%'),
                ICD10Code.description.ilike(f'%{query}%')
            )
        ).limit(limit).all()

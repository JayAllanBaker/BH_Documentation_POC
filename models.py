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

    # Remove the existing unique constraint on email
    __table_args__ = (
        # Add a conditional unique index that only applies to non-null emails
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
    
    user = db.relationship('User', backref='audit_logs')

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

class PatientIdentifier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    identifier_type = db.Column(db.String(50), nullable=False)  # e.g., 'Claim', 'Medicare', 'Medicaid'
    identifier_value = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    identifiers = db.relationship('PatientIdentifier', backref='patient', lazy=True, cascade='all, delete-orphan')
    conditions = db.relationship('Condition', backref='patient', lazy=True, cascade='all, delete-orphan')

    @staticmethod
    def generate_identifier():
        # Get the latest patient ID and increment it
        latest_patient = Patient.query.order_by(Patient.id.desc()).first()
        if latest_patient:
            next_id = latest_patient.id + 1
        else:
            next_id = 1
        return f'P{next_id:06d}'  # Format: P000001, P000002, etc.

class Condition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # FHIR Condition.identifier
    identifier = db.Column(db.String(50), unique=True)
    # FHIR Condition.clinicalStatus
    clinical_status = db.Column(db.String(50), nullable=False)  # active, recurrence, relapse, inactive, remission, resolved
    # FHIR Condition.verificationStatus
    verification_status = db.Column(db.String(50))  # unconfirmed, provisional, differential, confirmed, refuted, entered-in-error
    # FHIR Condition.category
    category = db.Column(db.String(50))  # problem-list-item, encounter-diagnosis
    # FHIR Condition.severity
    severity = db.Column(db.String(50))  # mild, moderate, severe
    # FHIR Condition.code
    code = db.Column(db.String(100))  # ICD-10 or SNOMED CT code
    code_system = db.Column(db.String(100))  # e.g., 'http://snomed.info/sct'
    # FHIR Condition.bodySite
    body_site = db.Column(db.String(100))
    # FHIR Condition.subject
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    # FHIR Condition.onset[x]
    onset_date = db.Column(db.Date)
    onset_string = db.Column(db.String(200))
    # FHIR Condition.abatement[x]
    abatement_date = db.Column(db.Date)
    abatement_string = db.Column(db.String(200))
    # FHIR Condition.recordedDate
    recorded_date = db.Column(db.DateTime, default=datetime.utcnow)
    # Additional fields
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def generate_identifier():
        latest_condition = Condition.query.order_by(Condition.id.desc()).first()
        if latest_condition:
            next_id = latest_condition.id + 1
        else:
            next_id = 1
        return f'C{next_id:06d}'  # Format: C000001, C000002, etc.

class ICD10Code(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def search_codes(query, limit=10):
        return ICD10Code.query.filter(
            or_(
                ICD10Code.code.ilike(f'{query}%'),
                ICD10Code.description.ilike(f'%{query}%')
            )
        ).limit(limit).all()

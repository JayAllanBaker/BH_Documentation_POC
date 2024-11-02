from functools import wraps
from flask import request, current_app
from flask_login import current_user
from models import db, AuditLog, Patient, Document, Condition
import json

def audit_log(action, resource_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                resource_id = kwargs.get('id')
                before_value = None
                after_value = None

                if action == 'view':
                    if resource_type == 'patient':
                        patient = Patient.query.get(resource_id)
                        after_value = {
                            'action': 'View patient details',
                            'patient_name': f'{patient.family_name}, {patient.given_name}',
                            'id': patient.identifier,
                            'type': 'Patient record view'
                        }
                    elif resource_type == 'document':
                        document = Document.query.get(resource_id)
                        after_value = {
                            'action': 'View document',
                            'title': document.title,
                            'patient': f'{document.patient.family_name}, {document.patient.given_name}' if document.patient else 'No patient',
                            'type': 'Document view'
                        }
                    elif resource_type == 'condition':
                        condition = Condition.query.get(resource_id)
                        after_value = {
                            'action': 'View condition',
                            'code': condition.code,
                            'description': condition.notes,
                            'patient': f'{condition.patient.family_name}, {condition.patient.given_name}',
                            'type': 'Condition view'
                        }
                elif action == 'edit' and request.method == 'POST':
                    if resource_type == 'patient':
                        original = Patient.query.get(resource_id)
                        before_value = {
                            'name': f'{original.family_name}, {original.given_name}',
                            'gender': original.gender,
                            'email': original.email,
                            'phone': original.phone,
                            'address': original.address_line
                        }
                    elif resource_type == 'document':
                        original = Document.query.get(resource_id)
                        before_value = {
                            'title': original.title,
                            'content': original.content,
                            'transcription': original.transcription
                        }
                    elif resource_type == 'condition':
                        original = Condition.query.get(resource_id)
                        before_value = {
                            'code': original.code,
                            'status': original.clinical_status,
                            'severity': original.severity,
                            'notes': original.notes
                        }
                    after_value = dict(request.form)
                elif action == 'search':
                    after_value = {
                        'action': 'Perform search',
                        'query': str(request.args.get('q', '')),
                        'type': str(request.args.get('type', 'all'))
                    }

                result = f(*args, **kwargs)
                
                # Create audit log entry
                log = AuditLog(
                    user_id=current_user.id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=str(request.form if request.form else request.args),
                    before_value=json.dumps(before_value) if before_value else None,
                    after_value=json.dumps(after_value) if after_value else None,
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string
                )
                db.session.add(log)
                db.session.commit()
                
                return result
            except Exception as e:
                current_app.logger.error(f'Error in audit log: {str(e)}')
                raise
        return decorated_function
    return decorator

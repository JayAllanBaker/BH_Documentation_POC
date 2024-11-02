from functools import wraps
from flask import request, current_app
from flask_login import current_user
from models import db, AuditLog

def audit_log(action, resource_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                
                # Create audit log entry
                log = AuditLog(
                    user_id=current_user.id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=kwargs.get('id'),
                    details=str(request.form if request.form else request.args),
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

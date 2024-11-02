from functools import wraps
from flask import request, current_app
from flask_login import current_user
from models import db, AuditLog

def audit_log(action, resource_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # For search actions, capture search parameters
                if action == 'search':
                    before_value = None
                    after_value = str(request.args)
                # For view actions, capture resource details
                elif action == 'view':
                    resource_id = kwargs.get('id')
                    before_value = None
                    after_value = f'Viewed {resource_type} #{resource_id}'
                # For update actions, capture changes
                else:
                    before_value = str(request.form.get('original_data', ''))
                    after_value = str(request.form)

                result = f(*args, **kwargs)
                
                log = AuditLog(
                    user_id=current_user.id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=kwargs.get('id'),
                    details=str(request.form if request.form else request.args),
                    before_value=before_value,
                    after_value=after_value,
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

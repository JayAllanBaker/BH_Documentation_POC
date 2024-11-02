from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from models import User, AuditLog, db
from functools import wraps
from sqlalchemy import or_

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/admin/audit-logs')
@login_required
@admin_required
def audit_logs():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '')
    
    logs_query = AuditLog.query.order_by(AuditLog.timestamp.desc())
    
    if query:
        logs_query = logs_query.filter(
            or_(
                AuditLog.action.ilike(f'%{query}%'),
                AuditLog.resource_type.ilike(f'%{query}%'),
                AuditLog.details.ilike(f'%{query}%')
            )
        )
    
    logs = logs_query.paginate(page=page, per_page=50)
    return render_template('admin/audit_logs.html', logs=logs, query=query)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.username).all()
    return render_template('admin/users/list.html', users=users)

@admin_bp.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('admin.create_user'))
            
        try:
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('User created successfully', 'success')
            return redirect(url_for('admin.list_users'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating user: {str(e)}')
            flash('An error occurred while creating the user', 'danger')
            
    return render_template('admin/users/new.html')

@admin_bp.route('/admin/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            user.username = request.form.get('username')
            user.email = request.form.get('email')
            user.role = request.form.get('role', 'user')
            
            new_password = request.form.get('password')
            if new_password:
                user.set_password(new_password)
                
            db.session.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('admin.list_users'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating user: {str(e)}')
            flash('An error occurred while updating the user', 'danger')
            
    return render_template('admin/users/edit.html', user=user)

@admin_bp.route('/admin/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    if current_user.id == id:
        flash('Cannot delete your own account', 'danger')
        return redirect(url_for('admin.list_users'))
        
    user = User.query.get_or_404(id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting user: {str(e)}')
        flash('An error occurred while deleting the user', 'danger')
        
    return redirect(url_for('admin.list_users'))

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_required, current_user
from models import User, AuditLog, db, AssessmentTool, AssessmentQuestion
from functools import wraps
from sqlalchemy import or_
from datetime import datetime
import json

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

@admin_bp.route('/admin/assessment-tools')
@login_required
@admin_required
def list_assessment_tools():
    tools = AssessmentTool.query.order_by(AssessmentTool.name).all()
    return render_template('admin/assessment_tools/list.html', tools=tools)

@admin_bp.route('/admin/assessment-tools/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_assessment_tool():
    if request.method == 'POST':
        try:
            scoring_logic = request.form.get('scoring_logic')
            if scoring_logic:
                try:
                    scoring_logic = json.loads(scoring_logic)
                except json.JSONDecodeError:
                    flash('Invalid JSON format for scoring logic', 'danger')
                    return render_template('admin/assessment_tools/edit.html')

            tool = AssessmentTool(
                name=request.form.get('name'),
                description=request.form.get('description'),
                version=request.form.get('version'),
                tool_type=request.form.get('tool_type'),
                scoring_logic=scoring_logic,
                active=bool(request.form.get('active'))
            )
            db.session.add(tool)
            db.session.commit()
            flash('Assessment tool created successfully', 'success')
            return redirect(url_for('admin.list_assessment_tools'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating assessment tool: {str(e)}')
            flash('An error occurred while creating the assessment tool', 'danger')
            
    return render_template('admin/assessment_tools/edit.html')

@admin_bp.route('/admin/assessment-tools/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_assessment_tool(id):
    tool = AssessmentTool.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            scoring_logic = request.form.get('scoring_logic')
            if scoring_logic:
                try:
                    scoring_logic = json.loads(scoring_logic)
                except json.JSONDecodeError:
                    flash('Invalid JSON format for scoring logic', 'danger')
                    return render_template('admin/assessment_tools/edit.html', tool=tool)

            tool.name = request.form.get('name')
            tool.description = request.form.get('description')
            tool.version = request.form.get('version')
            tool.tool_type = request.form.get('tool_type')
            tool.scoring_logic = scoring_logic
            tool.active = bool(request.form.get('active'))
            
            db.session.commit()
            flash('Assessment tool updated successfully', 'success')
            return redirect(url_for('admin.list_assessment_tools'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating assessment tool: {str(e)}')
            flash('An error occurred while updating the assessment tool', 'danger')
            
    return render_template('admin/assessment_tools/edit.html', tool=tool)

@admin_bp.route('/admin/assessment-tools/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_assessment_tool(id):
    tool = AssessmentTool.query.get_or_404(id)
    try:
        db.session.delete(tool)
        db.session.commit()
        flash('Assessment tool deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting assessment tool: {str(e)}')
        flash('An error occurred while deleting the assessment tool', 'danger')
    return redirect(url_for('admin.list_assessment_tools'))

@admin_bp.route('/admin/assessment-tools/<int:id>/questions/add', methods=['POST'])
@login_required
@admin_required
def add_question(id):
    tool = AssessmentTool.query.get_or_404(id)
    
    try:
        options = request.form.get('options')
        if options:
            try:
                options = json.loads(options)
            except json.JSONDecodeError:
                flash('Invalid JSON format for options', 'danger')
                return redirect(url_for('admin.edit_assessment_tool', id=id))

        question = AssessmentQuestion(
            tool_id=tool.id,
            question_text=request.form.get('question_text'),
            order=request.form.get('order', type=int),
            question_type=request.form.get('question_type'),
            options=options,
            required=bool(request.form.get('required')),
            help_text=request.form.get('help_text')
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error adding question: {str(e)}')
        flash('An error occurred while adding the question', 'danger')
        
    return redirect(url_for('admin.edit_assessment_tool', id=id))

@admin_bp.route('/admin/questions/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_question(id):
    question = AssessmentQuestion.query.get_or_404(id)
    
    try:
        options = request.form.get('options')
        if options:
            try:
                options = json.loads(options)
            except json.JSONDecodeError:
                flash('Invalid JSON format for options', 'danger')
                return redirect(url_for('admin.edit_assessment_tool', id=question.tool_id))

        question.question_text = request.form.get('question_text')
        question.order = request.form.get('order', type=int)
        question.question_type = request.form.get('question_type')
        question.options = options
        question.required = bool(request.form.get('required'))
        question.help_text = request.form.get('help_text')
        
        db.session.commit()
        flash('Question updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating question: {str(e)}')
        flash('An error occurred while updating the question', 'danger')
        
    return redirect(url_for('admin.edit_assessment_tool', id=question.tool_id))

@admin_bp.route('/admin/questions/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_question(id):
    question = AssessmentQuestion.query.get_or_404(id)
    tool_id = question.tool_id
    
    try:
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting question: {str(e)}')
        flash('An error occurred while deleting the question', 'danger')
        
    return redirect(url_for('admin.edit_assessment_tool', id=tool_id))

@admin_bp.route('/admin/questions/<int:id>/details')
@login_required
@admin_required
def get_question_details(id):
    question = AssessmentQuestion.query.get_or_404(id)
    return jsonify({
        'question_text': question.question_text,
        'help_text': question.help_text,
        'question_type': question.question_type,
        'order': question.order,
        'options': question.options,
        'required': question.required
    })

# User management routes
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
            user = User()
            user.username = username
            user.email = email
            user.role = role
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

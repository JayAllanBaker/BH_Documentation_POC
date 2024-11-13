from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Document, Patient, AssessmentResult, AssessmentTool
from sqlalchemy import func
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Recent documents
    recent_documents = Document.query.filter_by(user_id=current_user.id)\
        .order_by(Document.updated_at.desc())\
        .limit(5).all()
    
    # Recent patients
    recent_patients = Patient.query.order_by(Patient.updated_at.desc())\
        .limit(5).all()
    
    # Recent assessments
    recent_assessments = AssessmentResult.query\
        .filter_by(assessor_id=current_user.id)\
        .order_by(AssessmentResult.assessment_date.desc())\
        .limit(5).all()
    
    # Assessment statistics
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)
    
    # Total assessments count
    total_assessments = AssessmentResult.query\
        .filter_by(assessor_id=current_user.id)\
        .count()
    
    # This month's assessments count
    monthly_assessments = AssessmentResult.query\
        .filter(AssessmentResult.assessor_id == current_user.id,
                func.date(AssessmentResult.assessment_date) >= month_start)\
        .count()
    
    # Draft assessments count
    draft_assessments = AssessmentResult.query\
        .filter_by(assessor_id=current_user.id, status='draft')\
        .count()
    
    # Available assessment tools
    assessment_tools = AssessmentTool.query\
        .filter_by(active=True)\
        .order_by(AssessmentTool.name)\
        .all()
    
    return render_template('dashboard.html',
                         documents=recent_documents,
                         patients=recent_patients,
                         recent_assessments=recent_assessments,
                         total_assessments=total_assessments,
                         monthly_assessments=monthly_assessments,
                         draft_assessments=draft_assessments,
                         assessment_tools=assessment_tools)

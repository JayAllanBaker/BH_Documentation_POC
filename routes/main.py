from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Document, Patient

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    recent_documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.updated_at.desc()).limit(5).all()
    recent_patients = Patient.query.order_by(Patient.updated_at.desc()).limit(5).all()
    return render_template('dashboard.html', documents=recent_documents, patients=recent_patients)

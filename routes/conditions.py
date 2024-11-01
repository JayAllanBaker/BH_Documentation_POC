from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required
from models import Patient, Condition, db
from datetime import datetime

conditions_bp = Blueprint('conditions', __name__)

@conditions_bp.route('/patients/<int:patient_id>/conditions')
@login_required
def list_conditions(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    conditions = Condition.query.filter_by(patient_id=patient_id).all()
    return render_template('conditions/list.html', patient=patient, conditions=conditions)

@conditions_bp.route('/patients/<int:patient_id>/conditions/new', methods=['GET', 'POST'])
@login_required
def create_condition(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            condition = Condition(
                identifier=Condition.generate_identifier(),
                clinical_status=request.form.get('clinical_status'),
                verification_status=request.form.get('verification_status'),
                category=request.form.get('category'),
                severity=request.form.get('severity'),
                code=request.form.get('code'),
                code_system=request.form.get('code_system'),
                body_site=request.form.get('body_site'),
                patient_id=patient_id,
                onset_date=datetime.strptime(request.form.get('onset_date'), '%Y-%m-%d').date() if request.form.get('onset_date') else None,
                onset_string=request.form.get('onset_string'),
                abatement_date=datetime.strptime(request.form.get('abatement_date'), '%Y-%m-%d').date() if request.form.get('abatement_date') else None,
                abatement_string=request.form.get('abatement_string'),
                notes=request.form.get('notes')
            )
            db.session.add(condition)
            db.session.commit()
            flash('Condition added successfully', 'success')
            return redirect(url_for('conditions.list_conditions', patient_id=patient_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating condition: {str(e)}')
            flash('An error occurred while creating the condition', 'danger')
            
    return render_template('conditions/new.html', patient=patient)

@conditions_bp.route('/conditions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_condition(id):
    condition = Condition.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            condition.clinical_status = request.form.get('clinical_status')
            condition.verification_status = request.form.get('verification_status')
            condition.category = request.form.get('category')
            condition.severity = request.form.get('severity')
            condition.code = request.form.get('code')
            condition.code_system = request.form.get('code_system')
            condition.body_site = request.form.get('body_site')
            
            onset_date = request.form.get('onset_date')
            if onset_date:
                condition.onset_date = datetime.strptime(onset_date, '%Y-%m-%d').date()
            condition.onset_string = request.form.get('onset_string')
            
            abatement_date = request.form.get('abatement_date')
            if abatement_date:
                condition.abatement_date = datetime.strptime(abatement_date, '%Y-%m-%d').date()
            condition.abatement_string = request.form.get('abatement_string')
            
            condition.notes = request.form.get('notes')
            condition.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Condition updated successfully', 'success')
            return redirect(url_for('conditions.list_conditions', patient_id=condition.patient_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating condition: {str(e)}')
            flash('An error occurred while updating the condition', 'danger')
            
    return render_template('conditions/edit.html', condition=condition)

@conditions_bp.route('/conditions/<int:id>/delete', methods=['POST'])
@login_required
def delete_condition(id):
    condition = Condition.query.get_or_404(id)
    patient_id = condition.patient_id
    
    try:
        db.session.delete(condition)
        db.session.commit()
        flash('Condition deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting condition: {str(e)}')
        flash('An error occurred while deleting the condition', 'danger')
        
    return redirect(url_for('conditions.list_conditions', patient_id=patient_id))

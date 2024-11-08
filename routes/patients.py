from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required
from models import Patient, PatientIdentifier, db
from utils.audit import audit_log
from datetime import datetime

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/patients')
@login_required
def list_patients():
    patients = Patient.query.filter_by(active=True).order_by(Patient.family_name).all()
    return render_template('patients/list.html', patients=patients)

@patients_bp.route('/patients/<int:id>')
@login_required
def view_patient(id):
    patient = Patient.query.get_or_404(id)
    return render_template('patients/view.html', patient=patient)

@patients_bp.route('/patients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@audit_log(action='edit', resource_type='patient')
def edit_patient(id):
    patient = Patient.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Get original data for audit log
            request.form = request.form.copy()
            request.form['original_data'] = {
                'name': f'{patient.family_name}, {patient.given_name}',
                'gender': patient.gender,
                'email': patient.email,
                'phone': patient.phone,
                'address': patient.address_line,
                'city': patient.city,
                'state': patient.state
            }
            
            # Update patient data
            patient.family_name = request.form.get('family_name')
            patient.given_name = request.form.get('given_name')
            patient.gender = request.form.get('gender')
            patient.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date() if request.form.get('birth_date') else None
            patient.phone = request.form.get('phone')
            patient.email = request.form.get('email')
            patient.address_line = request.form.get('address_line')
            patient.city = request.form.get('city')
            patient.state = request.form.get('state')
            patient.postal_code = request.form.get('postal_code')
            patient.country = request.form.get('country')
            
            db.session.commit()
            flash('Patient updated successfully', 'success')
            return redirect(url_for('patients.view_patient', id=id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating patient: {str(e)}')
            flash('An error occurred while updating the patient', 'danger')
            
    return render_template('patients/edit.html', patient=patient)

@patients_bp.route('/patients/<int:id>/identifiers/add', methods=['POST'])
@login_required
@audit_log(action='create', resource_type='patient_identifier')
def add_identifier(id):
    patient = Patient.query.get_or_404(id)
    
    try:
        identifier = PatientIdentifier(
            patient_id=patient.id,
            identifier_type=request.form.get('identifier_type'),
            identifier_value=request.form.get('identifier_value')
        )
        db.session.add(identifier)
        db.session.commit()
        flash('Identifier added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error adding identifier: {str(e)}')
        flash('An error occurred while adding the identifier', 'danger')
        
    return redirect(url_for('patients.view_patient', id=id))

@patients_bp.route('/patients/<int:id>/identifiers/edit', methods=['POST'])
@login_required
@audit_log(action='edit', resource_type='patient_identifier')
def edit_identifier(id):
    patient = Patient.query.get_or_404(id)
    identifier_id = request.form.get('identifier_id')
    identifier = PatientIdentifier.query.get_or_404(identifier_id)
    
    if identifier.patient_id != patient.id:
        flash('Access denied', 'danger')
        return redirect(url_for('patients.view_patient', id=id))
    
    try:
        identifier.identifier_type = request.form.get('identifier_type')
        identifier.identifier_value = request.form.get('identifier_value')
        db.session.commit()
        flash('Identifier updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating identifier: {str(e)}')
        flash('An error occurred while updating the identifier', 'danger')
        
    return redirect(url_for('patients.view_patient', id=id))

@patients_bp.route('/identifiers/<int:id>/delete', methods=['POST'])
@login_required
@audit_log(action='delete', resource_type='patient_identifier')
def delete_identifier(id):
    identifier = PatientIdentifier.query.get_or_404(id)
    patient_id = identifier.patient_id
    
    try:
        db.session.delete(identifier)
        db.session.commit()
        flash('Identifier deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting identifier: {str(e)}')
        flash('An error occurred while deleting the identifier', 'danger')
        
    return redirect(url_for('patients.view_patient', id=patient_id))

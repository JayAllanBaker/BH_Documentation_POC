from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required
from models import Patient, PatientIdentifier, db
from datetime import datetime

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/patients')
@login_required
def list_patients():
    patients = Patient.query.filter_by(active=True).all()
    return render_template('patients/list.html', patients=patients)

@patients_bp.route('/patients/new', methods=['GET', 'POST'])
@login_required
def create_patient():
    if request.method == 'POST':
        try:
            # Get form data
            family_name = request.form.get('family_name')
            given_name = request.form.get('given_name')
            gender = request.form.get('gender')
            birth_date_str = request.form.get('birth_date')
            
            # Validate required fields
            form_errors = not all([family_name, given_name, gender, birth_date_str])
            if form_errors:
                flash('Please fill in all required fields', 'danger')
                return render_template('patients/new.html', 
                    form_errors=True,
                    family_name=family_name,
                    given_name=given_name,
                    gender=gender,
                    birth_date=birth_date_str,
                    phone=request.form.get('phone'),
                    email=request.form.get('email'),
                    address_line=request.form.get('address_line'),
                    city=request.form.get('city'),
                    state=request.form.get('state'),
                    postal_code=request.form.get('postal_code'),
                    country=request.form.get('country'))

            # Convert birth_date string to date object
            birth_date = None
            try:
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            except ValueError as e:
                current_app.logger.error(f'Invalid date format: {str(e)}')
                flash('Invalid date format', 'danger')
                return render_template('patients/new.html', 
                    form_errors=True,
                    family_name=family_name,
                    given_name=given_name,
                    gender=gender,
                    birth_date=birth_date_str,
                    phone=request.form.get('phone'),
                    email=request.form.get('email'),
                    address_line=request.form.get('address_line'),
                    city=request.form.get('city'),
                    state=request.form.get('state'),
                    postal_code=request.form.get('postal_code'),
                    country=request.form.get('country'))

            # Create new patient with auto-generated identifier
            patient = Patient(
                identifier=Patient.generate_identifier(),
                family_name=family_name,
                given_name=given_name,
                gender=gender,
                birth_date=birth_date,
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                address_line=request.form.get('address_line'),
                city=request.form.get('city'),
                state=request.form.get('state'),
                postal_code=request.form.get('postal_code'),
                country=request.form.get('country')
            )
            
            # Add the patient first to get the ID
            db.session.add(patient)
            db.session.flush()

            # Handle additional identifiers
            identifier_types = request.form.getlist('identifier_types[]')
            identifier_values = request.form.getlist('identifier_values[]')
            
            for type_, value in zip(identifier_types, identifier_values):
                if type_ and value:
                    patient_identifier = PatientIdentifier(
                        patient_id=patient.id,
                        identifier_type=type_,
                        identifier_value=value
                    )
                    db.session.add(patient_identifier)

            db.session.commit()
            current_app.logger.info(f'Patient created successfully: {patient.identifier}')
            flash('Patient created successfully', 'success')
            return redirect(url_for('patients.list_patients'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating patient: {str(e)}')
            flash('An error occurred while creating the patient', 'danger')
            return render_template('patients/new.html', 
                form_errors=True,
                family_name=family_name,
                given_name=given_name,
                gender=gender,
                birth_date=birth_date_str,
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                address_line=request.form.get('address_line'),
                city=request.form.get('city'),
                state=request.form.get('state'),
                postal_code=request.form.get('postal_code'),
                country=request.form.get('country'))
            
    return render_template('patients/new.html')

@patients_bp.route('/patients/<int:id>')
@login_required
def view_patient(id):
    patient = Patient.query.get_or_404(id)
    return render_template('patients/view.html', patient=patient)

@patients_bp.route('/patients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(id):
    patient = Patient.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # Convert birth_date string to date object
            birth_date = None
            birth_date_str = request.form.get('birth_date')
            if birth_date_str:
                try:
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                except ValueError as e:
                    current_app.logger.error(f'Invalid date format: {str(e)}')
                    flash('Invalid date format', 'danger')
                    return render_template('patients/edit.html', patient=patient)

            # Update patient basic info
            patient.family_name = request.form.get('family_name')
            patient.given_name = request.form.get('given_name')
            patient.gender = request.form.get('gender')
            patient.birth_date = birth_date
            patient.phone = request.form.get('phone')
            patient.email = request.form.get('email')
            patient.address_line = request.form.get('address_line')
            patient.city = request.form.get('city')
            patient.state = request.form.get('state')
            patient.postal_code = request.form.get('postal_code')
            patient.country = request.form.get('country')

            # Handle identifiers
            # First, remove all existing identifiers
            PatientIdentifier.query.filter_by(patient_id=patient.id).delete()

            # Then add the new ones
            identifier_types = request.form.getlist('identifier_types[]')
            identifier_values = request.form.getlist('identifier_values[]')
            
            for type_, value in zip(identifier_types, identifier_values):
                if type_ and value:
                    patient_identifier = PatientIdentifier(
                        patient_id=patient.id,
                        identifier_type=type_,
                        identifier_value=value
                    )
                    db.session.add(patient_identifier)
            
            db.session.commit()
            current_app.logger.info(f'Patient updated successfully: {patient.identifier}')
            flash('Patient updated successfully', 'success')
            return redirect(url_for('patients.view_patient', id=id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating patient: {str(e)}')
            flash('An error occurred while updating the patient', 'danger')
            
    return render_template('patients/edit.html', patient=patient)

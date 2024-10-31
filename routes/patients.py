from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required
from models import Patient, db
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
            identifier = request.form.get('identifier')
            family_name = request.form.get('family_name')
            given_name = request.form.get('given_name')
            
            # Validate required fields
            if not all([identifier, family_name, given_name]):
                flash('Patient ID, Family Name, and Given Name are required fields')
                return render_template('patients/new.html')
            
            # Check for duplicate identifier
            if Patient.query.filter_by(identifier=identifier).first():
                flash('A patient with this ID already exists')
                return render_template('patients/new.html')

            # Convert birth_date string to date object
            birth_date = None
            birth_date_str = request.form.get('birth_date')
            if birth_date_str:
                try:
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                except ValueError as e:
                    current_app.logger.error(f'Invalid date format: {str(e)}')
                    flash('Invalid date format')
                    return render_template('patients/new.html')

            # Create new patient
            patient = Patient(
                identifier=identifier,
                family_name=family_name,
                given_name=given_name,
                gender=request.form.get('gender'),
                birth_date=birth_date,
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                address_line=request.form.get('address_line'),
                city=request.form.get('city'),
                state=request.form.get('state'),
                postal_code=request.form.get('postal_code'),
                country=request.form.get('country')
            )
            
            db.session.add(patient)
            db.session.commit()
            current_app.logger.info(f'Patient created successfully: {identifier}')
            flash('Patient created successfully')
            return redirect(url_for('patients.list_patients'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating patient: {str(e)}')
            flash('An error occurred while creating the patient')
            return render_template('patients/new.html')
            
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
                    flash('Invalid date format')
                    return render_template('patients/edit.html', patient=patient)

            patient.identifier = request.form.get('identifier')
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
            
            db.session.commit()
            current_app.logger.info(f'Patient updated successfully: {patient.identifier}')
            flash('Patient updated successfully')
            return redirect(url_for('patients.view_patient', id=id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating patient: {str(e)}')
            flash('An error occurred while updating the patient')
            
    return render_template('patients/edit.html', patient=patient)

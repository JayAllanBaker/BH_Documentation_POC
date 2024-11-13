from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_required, current_user
from models import Patient, PatientIdentifier, AssessmentTool, AssessmentResult, AssessmentResponse, Document, db
from utils.audit import audit_log
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from utils.ai_analysis import extract_assessment_data

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

@patients_bp.route('/patients/new', methods=['GET', 'POST'])
@login_required
@audit_log(action='create', resource_type='patient')
def create_patient():
    if request.method == 'POST':
        try:
            birth_date_str = request.form.get('birth_date')
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else None
            
            patient = Patient()
            patient.identifier = Patient.generate_identifier()
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
            
            db.session.add(patient)
            db.session.commit()
            flash('Patient created successfully', 'success')
            return redirect(url_for('patients.view_patient', id=patient.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating patient: {str(e)}')
            flash('An error occurred while creating the patient', 'danger')
            
    return render_template('patients/new.html')

@patients_bp.route('/patients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@audit_log(action='edit', resource_type='patient')
def edit_patient(id):
    patient = Patient.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Store original data for audit log
            original_data = {
                'name': f'{patient.family_name}, {patient.given_name}',
                'gender': patient.gender,
                'email': patient.email,
                'phone': patient.phone,
                'address': patient.address_line,
                'city': patient.city,
                'state': patient.state
            }
            request.environ['audit_original_data'] = original_data
            
            birth_date_str = request.form.get('birth_date')
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else None
            
            # Update patient data
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
        identifier = PatientIdentifier()
        identifier.patient_id = patient.id
        identifier.identifier_type = request.form.get('identifier_type')
        identifier.identifier_value = request.form.get('identifier_value')
        
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

# Assessment routes
@patients_bp.route('/patients/<int:id>/assessments')
@login_required
def list_assessments(id):
    patient = Patient.query.get_or_404(id)
    assessment_tools = AssessmentTool.query.filter_by(active=True).order_by(AssessmentTool.name).all()
    return render_template('patients/assessments.html', patient=patient, assessment_tools=assessment_tools)

@patients_bp.route('/patients/<int:patient_id>/assessments/create', methods=['POST'])
@login_required
@audit_log(action='create', resource_type='assessment')
def create_assessment(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    tool_id = request.form.get('tool_id')
    tool = AssessmentTool.query.get_or_404(tool_id)
    
    try:
        result = AssessmentResult()
        result.patient_id = patient.id
        result.tool_id = tool.id
        result.assessor_id = current_user.id
        result.status = 'draft'
        
        db.session.add(result)
        db.session.commit()
        flash('Assessment started', 'success')
        return redirect(url_for('patients.edit_assessment', patient_id=patient.id, result_id=result.id))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error creating assessment: {str(e)}')
        flash('An error occurred while creating the assessment', 'danger')
        return redirect(url_for('patients.list_assessments', id=patient.id))

@patients_bp.route('/patients/<int:patient_id>/assessments/<int:result_id>')
@login_required
def view_assessment(patient_id, result_id):
    patient = Patient.query.get_or_404(patient_id)
    result = AssessmentResult.query.get_or_404(result_id)
    
    if result.patient_id != patient.id:
        flash('Access denied', 'danger')
        return redirect(url_for('patients.list_assessments', id=patient_id))
        
    return render_template('patients/assessment_view.html', patient=patient, result=result)

@patients_bp.route('/patients/<int:patient_id>/assessments/<int:result_id>/edit', methods=['GET', 'POST'])
@login_required
@audit_log(action='edit', resource_type='assessment')
def edit_assessment(patient_id, result_id):
    patient = Patient.query.get_or_404(patient_id)
    result = AssessmentResult.query.get_or_404(result_id)
    
    if result.patient_id != patient.id:
        flash('Access denied', 'danger')
        return redirect(url_for('patients.list_assessments', id=patient_id))
        
    if result.status != 'draft':
        flash('Cannot edit a completed assessment', 'danger')
        return redirect(url_for('patients.view_assessment', patient_id=patient_id, result_id=result_id))
    
    if request.method == 'POST':
        try:
            # Clear existing responses
            for response in result.responses:
                db.session.delete(response)
            
            # Add new responses
            for question in result.tool.questions:
                response_value = request.form.get(f'response_{question.id}')
                if response_value:
                    score = None
                    if question.options:
                        option = next((opt for opt in question.options if opt['value'] == response_value), None)
                        if option and 'score' in option:
                            score = float(option['score'])
                            
                    response = AssessmentResponse()
                    response.result_id = result.id
                    response.question_id = question.id
                    response.response_value = response_value
                    response.score = score
                    
                    db.session.add(response)
            
            result.clinical_notes = request.form.get('clinical_notes')
            
            # Handle action
            action = request.form.get('action')
            if action == 'complete':
                if not result.validate_responses():
                    flash('Please answer all required questions', 'danger')
                    db.session.rollback()
                    return render_template('patients/assessment_form.html', patient=patient, result=result)
                    
                result.status = 'completed'
                result.total_score = result.calculate_score()
                flash('Assessment completed', 'success')
            else:
                flash('Assessment saved', 'success')
                
            db.session.commit()
            
            if action == 'complete':
                return redirect(url_for('patients.view_assessment', patient_id=patient_id, result_id=result_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating assessment: {str(e)}')
            flash('An error occurred while updating the assessment', 'danger')
    
    return render_template('patients/assessment_form.html', patient=patient, result=result)

@patients_bp.route('/patients/<int:patient_id>/assessments/<int:result_id>/delete', methods=['POST'])
@login_required
@audit_log(action='delete', resource_type='assessment')
def delete_assessment(patient_id, result_id):
    patient = Patient.query.get_or_404(patient_id)
    result = AssessmentResult.query.get_or_404(result_id)
    
    if result.patient_id != patient.id:
        flash('Access denied', 'danger')
        return redirect(url_for('patients.list_assessments', id=patient_id))
        
    if result.status != 'draft':
        flash('Cannot delete a completed assessment', 'danger')
        return redirect(url_for('patients.list_assessments', id=patient_id))
    
    try:
        db.session.delete(result)
        db.session.commit()
        flash('Assessment deleted', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting assessment: {str(e)}')
        flash('An error occurred while deleting the assessment', 'danger')
        
    return redirect(url_for('patients.list_assessments', id=patient_id))

@patients_bp.route('/patients/<int:patient_id>/assessments/<int:result_id>/upload', methods=['POST'])
@login_required
@audit_log(action='upload', resource_type='assessment_document')
def upload_assessment_document(patient_id, result_id):
    patient = Patient.query.get_or_404(patient_id)
    result = AssessmentResult.query.get_or_404(result_id)
    
    if result.patient_id != patient.id:
        return jsonify({'error': 'Access denied'}), 403
        
    if result.status != 'draft':
        return jsonify({'error': 'Cannot modify a completed assessment'}), 400
    
    if 'document' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['document']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400
        
    try:
        # Save the document
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Create document record
        document = Document(
            title=f"Assessment Document - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            content="Uploaded for assessment",
            user_id=current_user.id,
            patient_id=patient.id
        )
        
        if file_path.lower().endswith(('.wav', '.mp3')):
            document.audio_file = filename
        else:
            with open(file_path, 'r') as f:
                document.content = f.read()
        
        db.session.add(document)
        db.session.flush()  # Get document ID
        
        # Process document content
        extracted_data = extract_assessment_data(file_path, result.tool)
        
        # Update assessment
        result.document_id = document.id
        result.entry_mode = 'document'
        
        # Clear existing responses
        for response in result.responses:
            db.session.delete(response)
            
        # Create new responses from extracted data
        for question_id, value in extracted_data.items():
            question = next((q for q in result.tool.questions if q.id == question_id), None)
            if question and value:
                score = None
                if question.options:
                    option = next((opt for opt in question.options if opt['value'] == str(value)), None)
                    if option and 'score' in option:
                        score = float(option['score'])
                        
                response = AssessmentResponse(
                    result_id=result.id,
                    question_id=question_id,
                    response_value=str(value),
                    score=score
                )
                db.session.add(response)
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error processing document: {str(e)}')
        return jsonify({'error': 'Error processing document'}), 500

@patients_bp.route('/patients/<int:patient_id>/assessments/<int:result_id>/remove-document', methods=['POST'])
@login_required
@audit_log(action='remove', resource_type='assessment_document')
def remove_assessment_document(patient_id, result_id):
    patient = Patient.query.get_or_404(patient_id)
    result = AssessmentResult.query.get_or_404(result_id)
    
    if result.patient_id != patient.id:
        return jsonify({'error': 'Access denied'}), 403
        
    if result.status != 'draft':
        return jsonify({'error': 'Cannot modify a completed assessment'}), 400
        
    try:
        # Clear document reference and responses
        result.document_id = None
        result.entry_mode = 'manual'
        
        for response in result.responses:
            db.session.delete(response)
            
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error removing document: {str(e)}')
        return jsonify({'error': 'Error removing document'}), 500
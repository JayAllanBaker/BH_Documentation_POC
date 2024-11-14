from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_required, current_user
from models import Patient, PatientIdentifier, AssessmentTool, AssessmentResult, AssessmentResponse, Document, db
from utils.audit import audit_log
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from utils.ai_analysis import extract_assessment_data

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/patients/<int:id>/identifiers')
@login_required
def list_identifiers(id):
    patient = Patient.query.get_or_404(id)
    identifiers = PatientIdentifier.query.filter_by(patient_id=patient.id).all()
    return render_template('patients/identifiers.html', patient=patient, identifiers=identifiers)

@patients_bp.route('/patients/<int:id>/identifiers/add', methods=['POST'])
@login_required
@audit_log(action='create', resource_type='patient_identifier')
def add_identifier(id):
    patient = Patient.query.get_or_404(id)
    identifier_type = request.form.get('type')
    identifier_value = request.form.get('value')
    
    if not identifier_type or not identifier_value:
        flash('Both type and value are required', 'danger')
        return redirect(url_for('patients.view_patient', id=id))
        
    try:
        identifier = PatientIdentifier()
        identifier.patient_id = patient.id
        identifier.identifier_type = identifier_type
        identifier.identifier_value = identifier_value
        db.session.add(identifier)
        db.session.commit()
        flash('Identifier added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error adding identifier: {str(e)}')
        flash('An error occurred while adding the identifier', 'danger')
        
    return redirect(url_for('patients.view_patient', id=id))

@patients_bp.route('/patients/<int:id>/identifiers/<int:identifier_id>/edit', methods=['POST'])
@login_required
@audit_log(action='edit', resource_type='patient_identifier')
def edit_identifier(id, identifier_id):
    patient = Patient.query.get_or_404(id)
    identifier = PatientIdentifier.query.get_or_404(identifier_id)
    
    if identifier.patient_id != patient.id:
        flash('Access denied', 'danger')
        return redirect(url_for('patients.view_patient', id=id))
        
    try:
        identifier.identifier_type = request.form.get('type')
        identifier.identifier_value = request.form.get('value')
        db.session.commit()
        flash('Identifier updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating identifier: {str(e)}')
        flash('An error occurred while updating the identifier', 'danger')
        
    return redirect(url_for('patients.view_patient', id=id))

@patients_bp.route('/patients/<int:id>/identifiers/<int:identifier_id>/delete', methods=['POST'])
@login_required
@audit_log(action='delete', resource_type='patient_identifier')
def delete_identifier(id, identifier_id):
    patient = Patient.query.get_or_404(id)
    identifier = PatientIdentifier.query.get_or_404(identifier_id)
    
    if identifier.patient_id != patient.id:
        flash('Access denied', 'danger')
        return redirect(url_for('patients.view_patient', id=id))
        
    try:
        db.session.delete(identifier)
        db.session.commit()
        flash('Identifier deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting identifier: {str(e)}')
        flash('An error occurred while deleting the identifier', 'danger')
        
    return redirect(url_for('patients.view_patient', id=id))

@patients_bp.route('/patients/<int:id>/edit-identifier/<int:identifier_id>')
@login_required
def edit_identifier_modal(id, identifier_id):
    patient = Patient.query.get_or_404(id)
    identifier = PatientIdentifier.query.get_or_404(identifier_id)
    
    if identifier.patient_id != patient.id:
        flash('Access denied', 'danger')
        return redirect(url_for('patients.view_patient', id=id))
    
    return render_template('patients/edit_identifier_modal.html', 
                         patient=patient, 
                         identifier=identifier)

@patients_bp.route('/patients/<int:id>/add-identifier')
@login_required
def add_identifier_modal(id):
    patient = Patient.query.get_or_404(id)
    return render_template('patients/add_identifier_modal.html', patient=patient)

@patients_bp.route('/patients')
@login_required
def list_patients():
    patients = Patient.query.filter_by(active=True).order_by(Patient.family_name).all()
    return render_template('patients/list.html', patients=patients)

@patients_bp.route('/assessments/create', methods=['POST'])
@login_required
@audit_log(action='create', resource_type='assessment')
def create_assessment():
    tool_id = request.form.get('tool_id')
    patient_id = request.form.get('patient_id')
    
    if not tool_id:
        flash('Assessment tool not specified', 'danger')
        return redirect(url_for('patients.all_assessments'))
    
    if not patient_id:
        # Redirect to patient selection page
        return redirect(url_for('patients.select_patient_for_assessment', tool_id=tool_id))
    
    patient = Patient.query.get_or_404(patient_id)
    tool = AssessmentTool.query.get_or_404(tool_id)
    
    try:
        result = AssessmentResult()
        result.patient_id = patient.id
        result.tool_id = tool.id
        result.assessor_id = current_user.id
        result.status = 'draft'
        result.assessment_date = datetime.utcnow()
        
        db.session.add(result)
        db.session.commit()
        flash('Assessment started', 'success')
        return redirect(url_for('patients.edit_assessment', patient_id=patient.id, result_id=result.id))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error creating assessment: {str(e)}')
        flash('An error occurred while creating the assessment', 'danger')
        return redirect(url_for('patients.all_assessments'))

@patients_bp.route('/assessments/select-patient')
@login_required
def select_patient_for_assessment():
    tool_id = request.args.get('tool_id')
    if not tool_id:
        flash('Assessment tool not specified', 'danger')
        return redirect(url_for('patients.all_assessments'))
        
    patients = Patient.query.filter_by(active=True).order_by(Patient.family_name).all()
    tool = AssessmentTool.query.get_or_404(tool_id)
    
    return render_template('patients/select_patient.html', 
                         patients=patients, 
                         tool=tool)

@patients_bp.route('/patients/<int:id>')
@login_required
def view_patient(id):
    patient = Patient.query.get_or_404(id)
    assessment_tools = AssessmentTool.query.filter_by(active=True).order_by(AssessmentTool.name).all()
    return render_template('patients/view.html', patient=patient, assessment_tools=assessment_tools)

@patients_bp.route('/patients/new', methods=['GET', 'POST'])
@login_required
@audit_log(action='create', resource_type='patient')
def create_patient():
    if request.method == 'POST':
        try:
            birth_date_str = request.form.get('birth_date')
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else None
            
            patient = Patient()
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

@patients_bp.route('/patients/<int:patient_id>/assessments/<int:result_id>/edit', methods=['GET', 'POST'])
@login_required
@audit_log(action='edit', resource_type='assessment')
def edit_assessment(patient_id, result_id):
    patient = Patient.query.get_or_404(patient_id)
    result = AssessmentResult.query.get_or_404(result_id)
    
    if result.patient_id != patient.id:
        flash('Access denied', 'danger')
        return redirect(url_for('patients.patient_assessments', patient_id=patient_id))
        
    if result.status != 'draft':
        flash('Cannot edit a completed assessment', 'danger')
        return redirect(url_for('patients.view_assessment', patient_id=patient_id, result_id=result_id))
    
    if request.method == 'POST':
        try:
            # Store current responses before clearing
            current_responses = {
                resp.question_id: resp.response_value 
                for resp in result.responses
            }
            
            # Clear existing responses
            for response in result.responses:
                db.session.delete(response)
            
            # Add new responses
            has_all_required = True
            new_responses = []
            
            for question in result.tool.questions:
                response_value = request.form.get(f'response_{question.id}')
                if question.required and not response_value:
                    has_all_required = False
                    # Restore previous responses
                    for q_id, value in current_responses.items():
                        resp = AssessmentResponse()
                        resp.result_id = result.id
                        resp.question_id = q_id
                        resp.response_value = value
                        new_responses.append(resp)
                    break
                    
                if response_value:
                    resp = AssessmentResponse()
                    resp.result_id = result.id
                    resp.question_id = question.id
                    resp.response_value = response_value
                    
                    if question.options:
                        option = next((opt for opt in question.options if opt['value'] == response_value), None)
                        if option and 'score' in option:
                            resp.score = float(option['score'])
                    
                    new_responses.append(resp)
            
            if not has_all_required:
                # Rollback and restore previous state
                db.session.rollback()
                flash('Please answer all required questions', 'danger')
                return render_template('patients/assessment_form.html', 
                                    patient=patient, 
                                    result=result)
            
            # Add all new responses
            for resp in new_responses:
                db.session.add(resp)
            
            result.clinical_notes = request.form.get('clinical_notes')
            
            # Handle action
            action = request.form.get('action')
            if action == 'complete':
                result.status = 'completed'
                # Calculate and set total score before commit
                result.total_score = sum(float(resp.score) for resp in new_responses if resp.score is not None)
                flash('Assessment completed', 'success')
            else:
                flash('Assessment saved', 'success')
                
            db.session.commit()
            
            if action == 'complete':
                return redirect(url_for('patients.view_assessment', 
                                      patient_id=patient_id, 
                                      result_id=result_id))
                                      
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating assessment: {str(e)}')
            flash('An error occurred while updating the assessment', 'danger')
    
    return render_template('patients/assessment_form.html', 
                         patient=patient, 
                         result=result)

@patients_bp.route('/patients/<int:patient_id>/assessments')
@login_required
def patient_assessments(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    assessment_tools = AssessmentTool.query.filter_by(active=True).order_by(AssessmentTool.name).all()
    return render_template('patients/assessments.html', 
                         patient=patient,
                         assessment_tools=assessment_tools)

@patients_bp.route('/assessments')
@login_required
def all_assessments():
    page = request.args.get('page', 1, type=int)
    query = AssessmentResult.query
    
    # Apply filters
    patient_query = request.args.get('patient')
    if patient_query:
        query = query.join(Patient).filter(
            db.or_(
                Patient.family_name.ilike(f'%{patient_query}%'),
                Patient.given_name.ilike(f'%{patient_query}%')
            )
        )
        
    tool_id = request.args.get('tool', type=int)
    if tool_id:
        query = query.filter(AssessmentResult.tool_id == tool_id)
        
    status = request.args.get('status')
    if status:
        query = query.filter(AssessmentResult.status == status)
        
    date_from = request.args.get('date_from')
    if date_from:
        query = query.filter(AssessmentResult.assessment_date >= datetime.strptime(date_from, '%Y-%m-%d'))
        
    date_to = request.args.get('date_to')
    if date_to:
        query = query.filter(AssessmentResult.assessment_date <= datetime.strptime(date_to, '%Y-%m-%d'))
        
    # Apply sorting
    sort = request.args.get('sort')
    order = request.args.get('order', 'asc')
    
    if sort == 'date':
        query = query.order_by(
            AssessmentResult.assessment_date.desc() if order == 'desc' 
            else AssessmentResult.assessment_date.asc()
        )
    elif sort == 'patient':
        query = query.join(Patient).order_by(
            Patient.family_name.desc() if order == 'desc'
            else Patient.family_name.asc()
        )
    elif sort == 'type':
        query = query.join(AssessmentTool).order_by(
            AssessmentTool.name.desc() if order == 'desc'
            else AssessmentTool.name.asc()
        )
    else:
        # Default sort by date descending
        query = query.order_by(AssessmentResult.assessment_date.desc())
    
    assessments = query.paginate(page=page, per_page=10)
    assessment_tools = AssessmentTool.query.filter_by(active=True).order_by(AssessmentTool.name).all()
    
    return render_template('patients/assessment_list.html',
                         assessments=assessments,
                         assessment_tools=assessment_tools)

@patients_bp.route('/patients/<int:patient_id>/assessments/<int:result_id>')
@login_required
def view_assessment(patient_id, result_id):
    patient = Patient.query.get_or_404(patient_id)
    result = AssessmentResult.query.get_or_404(result_id)
    
    if result.patient_id != patient.id:
        flash('Access denied', 'danger')
        return redirect(url_for('patients.patient_assessments', patient_id=patient_id))
        
    return render_template('patients/assessment_view.html',
                         patient=patient,
                         result=result)

@patients_bp.route('/patients/<int:patient_id>/assessments/<int:result_id>/delete', methods=['POST'])
@login_required
@audit_log(action='delete', resource_type='assessment')
def delete_assessment(patient_id, result_id):
    patient = Patient.query.get_or_404(patient_id)
    result = AssessmentResult.query.get_or_404(result_id)
    
    if result.patient_id != patient.id:
        flash('Access denied', 'danger')
        return redirect(url_for('patients.patient_assessments', patient_id=patient_id))
        
    if result.status != 'draft':
        flash('Cannot delete a completed assessment', 'danger')
        return redirect(url_for('patients.view_assessment', patient_id=patient_id, result_id=result_id))
        
    try:
        db.session.delete(result)
        db.session.commit()
        flash('Assessment deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting assessment: {str(e)}')
        flash('An error occurred while deleting the assessment', 'danger')
        
    return redirect(url_for('patients.patient_assessments', patient_id=patient_id))

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
    
    try:
        if 'document' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
            
        file = request.files['document']
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file selected'}), 400
            
        # Validate file type
        allowed_extensions = {'txt', 'doc', 'docx', 'pdf', 'wav', 'mp3'}
        if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
            
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with secure filename
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Process file and extract assessment data
        extracted_data = extract_assessment_data(filepath, result.tool_type)
        
        # Update assessment with extracted data
        for question_id, value in extracted_data.items():
            # Convert array responses to string format
            if isinstance(value, list):
                response_value = ', '.join(str(v) for v in value)
            else:
                response_value = str(value)
                
            response = AssessmentResponse(
                result_id=result.id,
                question_id=question_id,
                response_value=response_value
            )
            db.session.add(response)
            
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error processing document: {str(e)}')
        return jsonify({'success': False, 'error': 'An error occurred during upload'}), 500

@patients_bp.route('/patients/<int:patient_id>/assessments/<int:result_id>/remove-document', methods=['POST'])
@login_required
def remove_assessment_document(patient_id, result_id):
    patient = Patient.query.get_or_404(patient_id)
    result = AssessmentResult.query.get_or_404(result_id)
    
    if result.patient_id != patient.id:
        return jsonify({'error': 'Access denied'}), 403
        
    if result.status != 'draft':
        return jsonify({'error': 'Cannot modify a completed assessment'}), 400
    
    try:
        if result.document:
            # Remove the file if it exists
            if result.document.audio_file:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], result.document.audio_file)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Delete the document
            db.session.delete(result.document)
        
        # Clear responses and reset entry mode
        for response in result.responses:
            db.session.delete(response)
            
        result.document_id = None
        result.entry_mode = 'manual'
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error removing document: {str(e)}')
        return jsonify({'error': str(e)}), 500
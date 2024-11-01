from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import Document, Patient, Condition, db
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import openai
import json

documents_bp = Blueprint('documents', __name__)

def analyze_meat_criteria(text):
    client = openai.OpenAI()
    
    prompt = '''Analyze the following medical transcription and categorize the content into MEAT criteria.
    
    Transcription:
    {text}
    
    Please categorize the content into these sections:
    1. Monitoring: Vital signs, physical findings, symptoms, behaviors
    2. Assessment: Current clinical assessment, diagnosis updates
    3. Evaluation: Test results, responses to treatment
    4. Treatment: Medications, therapies, procedures, changes in treatment

    Return the response in this exact format with these exact section headers:
    Monitoring:
    <monitoring content>
    
    Assessment:
    <assessment content>
    
    Evaluation:
    <evaluation content>
    
    Treatment:
    <treatment content>'''

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a medical documentation assistant analyzing clinical notes for MEAT criteria."},
                {"role": "user", "content": prompt.format(text=text)}
            ]
        )
        
        # Parse the response text into sections
        response_text = response.choices[0].message.content
        sections = {}
        current_section = None
        current_content = []
        
        for line in response_text.split('\n'):
            line = line.strip()
            if line.endswith(':'):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[:-1].lower()
                current_content = []
            elif line and current_section:
                current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return {
            'monitoring': sections.get('monitoring', ''),
            'assessment': sections.get('assessment', ''),
            'evaluation': sections.get('evaluation', ''),
            'treatment': sections.get('treatment', '')
        }
    except Exception as e:
        current_app.logger.error(f'MEAT analysis error: {str(e)}')
        return None

def extract_conditions(text):
    client = openai.OpenAI()
    
    prompt = '''Extract medical conditions from the following transcription.
    For each condition, provide:
    1. ICD-10 or SNOMED CT code
    2. Clinical description
    3. Body site (if applicable)
    4. Severity (mild/moderate/severe if mentioned)

    Transcription:
    {text}

    Return the response in JSON format with an array of conditions:
    [
        {{
            "code": "ICD-10 or SNOMED code",
            "code_system": "ICD-10" or "SNOMED-CT",
            "description": "condition description",
            "body_site": "affected body part",
            "severity": "mild/moderate/severe"
        }},
        ...
    ]'''

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a medical coding specialist extracting and coding conditions from clinical notes."},
                {"role": "user", "content": prompt.format(text=text)}
            ]
        )
        
        # Parse the response text as JSON
        conditions = json.loads(response.choices[0].message.content)
        return conditions
    except Exception as e:
        current_app.logger.error(f'Condition extraction error: {str(e)}')
        return None

@documents_bp.route('/documents')
@login_required
def list_documents():
    documents = Document.query.filter_by(user_id=current_user.id).all()
    return render_template('documents/list.html', documents=documents)

@documents_bp.route('/documents/new', methods=['GET', 'POST'])
@login_required
def create_document():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            patient_id = request.form.get('patient_id')
            
            if not title:
                flash('Title is required', 'danger')
                return redirect(url_for('documents.create_document'))
            
            document = Document(
                title=title,
                user_id=current_user.id,
                patient_id=patient_id if patient_id else None
            )
            db.session.add(document)
            db.session.commit()
            flash('Document created successfully', 'success')
            return redirect(url_for('documents.edit_document', id=document.id))
        except Exception as e:
            current_app.logger.error(f'Error creating document: {str(e)}')
            flash('An error occurred while creating the document', 'danger')
            return redirect(url_for('documents.create_document'))
            
    patients = Patient.query.filter_by(active=True).order_by(Patient.family_name).all()
    return render_template('documents/new.html', patients=patients)

@documents_bp.route('/documents/<int:id>')
@login_required
def view_document(id):
    document = Document.query.get_or_404(id)
    if document.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('documents.list_documents'))
    return render_template('documents/view.html', document=document)

@documents_bp.route('/documents/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_document(id):
    document = Document.query.get_or_404(id)
    if document.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('documents.list_documents'))
    
    if request.method == 'POST':
        try:
            document.title = request.form.get('title')
            document.content = request.form.get('content')
            document.meat_monitoring = request.form.get('meat_monitoring')
            document.meat_assessment = request.form.get('meat_assessment')
            document.meat_evaluation = request.form.get('meat_evaluation')
            document.meat_treatment = request.form.get('meat_treatment')
            document.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Document updated successfully', 'success')
            return redirect(url_for('documents.view_document', id=id))
        except Exception as e:
            current_app.logger.error(f'Error updating document: {str(e)}')
            flash('An error occurred while updating the document', 'danger')
            return render_template('documents/edit.html', document=document)
    
    return render_template('documents/edit.html', document=document)

@documents_bp.route('/documents/<int:id>/upload-audio', methods=['POST'])
@login_required
def upload_audio(id):
    try:
        document = Document.query.get_or_404(id)
        if document.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403

        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if not audio_file:
            return jsonify({'error': 'No audio file provided'}), 400

        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"doc_{document.id}_{timestamp}.wav"
        filepath = os.path.join(uploads_dir, secure_filename(filename))

        # Save the audio file
        audio_file.save(filepath)
        document.audio_file = filename

        # Transcribe audio using OpenAI's new API format
        try:
            client = openai.OpenAI()
            with open(filepath, 'rb') as audio:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    response_format="text"
                )
                document.transcription = transcript

            # Perform MEAT analysis on the transcription
            meat_analysis = analyze_meat_criteria(transcript)
            if meat_analysis:
                document.meat_monitoring = meat_analysis.get('monitoring', '')
                document.meat_assessment = meat_analysis.get('assessment', '')
                document.meat_evaluation = meat_analysis.get('evaluation', '')
                document.meat_treatment = meat_analysis.get('treatment', '')

            # Extract and create conditions if document is linked to a patient
            conditions_created = []
            if document.patient_id:
                conditions = extract_conditions(transcript)
                if conditions:
                    for condition_data in conditions:
                        condition = Condition(
                            identifier=Condition.generate_identifier(),
                            clinical_status='active',
                            category='encounter-diagnosis',
                            code=condition_data.get('code'),
                            code_system=condition_data.get('code_system'),
                            body_site=condition_data.get('body_site'),
                            severity=condition_data.get('severity'),
                            patient_id=document.patient_id,
                            onset_date=datetime.utcnow().date(),
                            notes=condition_data.get('description')
                        )
                        db.session.add(condition)
                        conditions_created.append({
                            'code': condition.code,
                            'description': condition.notes,
                            'severity': condition.severity
                        })

            db.session.commit()
            return jsonify({
                'status': 'success',
                'filename': filename,
                'transcription': transcript,
                'meat_analysis': meat_analysis,
                'conditions_created': conditions_created
            })
        except Exception as e:
            current_app.logger.error(f'Transcription error: {str(e)}')
            return jsonify({'error': 'Error processing audio'}), 500

    except Exception as e:
        current_app.logger.error(f'Upload error: {str(e)}')
        return jsonify({'error': 'Error uploading audio'}), 500

@documents_bp.route('/documents/<int:id>/delete', methods=['POST'])
@login_required
def delete_document(id):
    document = Document.query.get_or_404(id)
    if document.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('documents.list_documents'))
    
    try:
        # Delete associated audio file if it exists
        if document.audio_file:
            audio_path = os.path.join(current_app.root_path, 'uploads', document.audio_file)
            if os.path.exists(audio_path):
                os.remove(audio_path)
        
        db.session.delete(document)
        db.session.commit()
        flash('Document deleted successfully', 'success')
    except Exception as e:
        current_app.logger.error(f'Error deleting document: {str(e)}')
        flash('An error occurred while deleting the document', 'danger')
    
    return redirect(url_for('documents.list_documents'))

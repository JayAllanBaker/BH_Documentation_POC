from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import Document, Patient, db
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import openai

documents_bp = Blueprint('documents', __name__)

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

        # Transcribe audio using OpenAI's Whisper API
        try:
            with open(filepath, 'rb') as audio:
                transcript = openai.Audio.transcribe("whisper-1", audio)
                transcription = transcript.text
                document.transcription = transcription

            db.session.commit()
            return jsonify({
                'status': 'success',
                'filename': filename,
                'transcription': transcription
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

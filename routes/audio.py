import os
import whisper
import logging
import json
from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import datetime
from app import db
from models import Document
from utils.ai_analysis import analyze_transcription

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

audio_bp = Blueprint('audio', __name__)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg'}
ALLOWED_MIMETYPES = {'audio/wav', 'audio/mpeg', 'audio/ogg'}
UPLOAD_FOLDER = 'uploads/audio'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = whisper.load_model("base")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_mimetype(mime_type):
    return mime_type in ALLOWED_MIMETYPES

@audio_bp.route('/api/audio/<int:doc_id>', methods=['GET'])
@login_required
def get_audio(doc_id):
    document = Document.query.get_or_404(doc_id)
    if document.author_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    if not document.recording_path or not os.path.exists(document.recording_path):
        return jsonify({'error': 'Audio not found'}), 404
    return send_file(document.recording_path)

@audio_bp.route('/api/upload-audio', methods=['POST'])
@login_required
def upload_audio():
    try:
        if 'audio' not in request.files:
            logger.error("No audio file in request")
            return jsonify({'error': 'No audio file provided'}), 400
            
        audio_file = request.files['audio']
        doc_id = request.form.get('document_id')
        
        if not doc_id:
            logger.error("Document ID is missing")
            return jsonify({'error': 'Document ID is required'}), 400
            
        if not doc_id.isdigit():
            logger.error(f"Invalid document ID format: {doc_id}")
            return jsonify({'error': 'Invalid document ID format'}), 400
            
        doc_id = int(doc_id)
        
        document = Document.query.get(doc_id)
        if not document:
            logger.error(f"Document not found: {doc_id}")
            return jsonify({'error': 'Document not found'}), 404
            
        if document.author_id != current_user.id:
            logger.error(f"Unauthorized access to document: {doc_id}")
            return jsonify({'error': 'Unauthorized access'}), 403
            
        if not audio_file or not audio_file.filename:
            logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_mimetype(audio_file.mimetype):
            logger.error(f"Invalid MIME type: {audio_file.mimetype}")
            return jsonify({'error': 'Invalid file type'}), 415

        if audio_file and allowed_file(audio_file.filename):
            filename = secure_filename(f"{current_user.id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            
            logger.info(f"Saving audio file to: {save_path}")
            audio_file.save(save_path)
            
            try:
                logger.info("Starting audio transcription")
                result = model.transcribe(save_path)
                transcription = result["text"]
                logger.info("Transcription completed successfully")
                
                document.recording_path = save_path
                document.transcription = transcription
                db.session.commit()
                logger.info("Document updated with transcription")
                
                return jsonify({
                    'filename': filename,
                    'transcription': transcription,
                    'status': 'success'
                }), 200
                    
            except Exception as e:
                logger.error(f"Transcription failed: {str(e)}")
                return jsonify({'error': f'Transcription failed: {str(e)}'}), 500
        
        logger.error("Invalid file type")
        return jsonify({'error': 'Invalid file type'}), 415
        
    except Exception as e:
        logger.error(f"Unexpected error in upload_audio: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@audio_bp.route('/api/generate-documentation', methods=['POST'])
@login_required
def generate_documentation():
    try:
        doc_id = request.json.get('document_id')
        if not doc_id:
            logger.error("No document ID provided")
            return jsonify({'error': 'No document ID provided'}), 400
            
        document = Document.query.get(doc_id)
        if not document or document.author_id != current_user.id:
            logger.error(f"Document not found or unauthorized. ID: {doc_id}")
            return jsonify({'error': 'Document not found or unauthorized'}), 404
            
        if not document.transcription:
            logger.error("No transcription available")
            return jsonify({'error': 'No transcription available'}), 400
            
        # Analyze transcription using AI
        logger.info(f"Analyzing transcription for document ID: {doc_id}")
        analysis_result = analyze_transcription(document.transcription)
        
        if not isinstance(analysis_result, dict):
            logger.error("Invalid analysis result format")
            return jsonify({'error': 'Invalid analysis result format'}), 500
        
        # Update document with AI analysis results
        document.meat_monitor = analysis_result.get('meat_monitor', '')
        document.meat_evaluate = analysis_result.get('meat_evaluate', '')
        document.meat_assess = analysis_result.get('meat_assess', '')
        document.meat_treat = analysis_result.get('meat_treat', '')
        document.tamper_time = analysis_result.get('tamper_time', '')
        document.tamper_action = analysis_result.get('tamper_action', '')
        document.tamper_medical_necessity = analysis_result.get('tamper_medical_necessity', '')
        document.tamper_plan = analysis_result.get('tamper_plan', '')
        document.tamper_education = analysis_result.get('tamper_education', '')
        document.tamper_response = analysis_result.get('tamper_response', '')
        
        db.session.commit()
        logger.info(f"Documentation generated for document ID: {doc_id}")
        
        return jsonify({
            'success': True,
            'analysis': analysis_result
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in generate_documentation: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

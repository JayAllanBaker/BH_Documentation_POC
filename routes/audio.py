import os
import whisper
import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import datetime
from app import db
from models import Document

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
            logger.error("No document ID provided")
            return jsonify({'error': 'No document ID provided'}), 400
            
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
            
            # Transcribe the audio
            try:
                logger.info("Starting audio transcription")
                result = model.transcribe(save_path)
                transcription = result["text"]
                logger.info("Transcription completed successfully")
                
                # Update the document with the recording path and transcription
                document = Document.query.get(doc_id)
                if document and document.author_id == current_user.id:
                    document.recording_path = save_path
                    document.transcription = transcription
                    db.session.commit()
                    logger.info("Document updated with transcription")
                    
                    return jsonify({
                        'filename': filename,
                        'transcription': transcription,
                        'status': 'success'
                    }), 200
                else:
                    logger.error(f"Document not found or unauthorized. ID: {doc_id}")
                    return jsonify({'error': 'Document not found or unauthorized'}), 404
                    
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
            
        # TODO: Implement MEAT/TAMPER analysis using the transcription
        document.content = document.transcription
        db.session.commit()
        logger.info(f"Documentation generated for document ID: {doc_id}")
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in generate_documentation: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

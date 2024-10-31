import os
import whisper
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import datetime
from app import db
from models import Document

audio_bp = Blueprint('audio', __name__)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg'}
UPLOAD_FOLDER = 'uploads/audio'
model = whisper.load_model("base")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@audio_bp.route('/api/upload-audio', methods=['POST'])
@login_required
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
        
    audio_file = request.files['audio']
    doc_id = request.form.get('document_id')
    
    if not doc_id:
        return jsonify({'error': 'No document ID provided'}), 400
        
    if audio_file and allowed_file(audio_file.filename):
        filename = secure_filename(f"{current_user.id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        audio_file.save(save_path)
        
        # Transcribe the audio
        try:
            result = model.transcribe(save_path)
            transcription = result["text"]
            
            # Update the document with the recording path and transcription
            document = Document.query.get(doc_id)
            if document and document.author_id == current_user.id:
                document.recording_path = save_path
                document.transcription = transcription
                db.session.commit()
                
                return jsonify({
                    'filename': filename,
                    'transcription': transcription
                })
            else:
                return jsonify({'error': 'Document not found or unauthorized'}), 404
                
        except Exception as e:
            return jsonify({'error': f'Transcription failed: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@audio_bp.route('/api/generate-documentation', methods=['POST'])
@login_required
def generate_documentation():
    doc_id = request.json.get('document_id')
    if not doc_id:
        return jsonify({'error': 'No document ID provided'}), 400
        
    document = Document.query.get(doc_id)
    if not document or document.author_id != current_user.id:
        return jsonify({'error': 'Document not found or unauthorized'}), 404
        
    if not document.transcription:
        return jsonify({'error': 'No transcription available'}), 400
        
    # TODO: Implement MEAT/TAMPER analysis using the transcription
    # For now, we'll just copy the transcription to the content
    document.content = document.transcription
    db.session.commit()
    
    return jsonify({'success': True})

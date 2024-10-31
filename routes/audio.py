import os
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import datetime

audio_bp = Blueprint('audio', __name__)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@audio_bp.route('/api/upload-audio', methods=['POST'])
@login_required
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
        
    audio_file = request.files['audio']
    if audio_file and allowed_file(audio_file.filename):
        filename = secure_filename(f"{current_user.id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
        save_path = os.path.join('uploads', 'audio', filename)
        audio_file.save(save_path)
        return jsonify({'filename': filename})
    
    return jsonify({'error': 'Invalid file type'}), 400

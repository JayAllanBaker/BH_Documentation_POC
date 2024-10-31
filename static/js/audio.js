class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.recordingTime = 0;
        this.recordingTimer = null;
        
        this.startButton = document.getElementById('startRecording');
        this.stopButton = document.getElementById('stopRecording');
        this.audioPlayer = document.getElementById('audioPlayer');
        this.transcriptionDisplay = document.getElementById('transcriptionDisplay');
        
        this.initializeButtons();
        this.setupStatusIndicator();
    }
    
    setupStatusIndicator() {
        this.statusIndicator = document.createElement('div');
        this.statusIndicator.className = 'alert mt-2 d-none';
        const parentNode = this.startButton.closest('.card-body');
        if (parentNode) {
            // Insert after the buttons but before the audio player
            parentNode.insertBefore(this.statusIndicator, this.audioPlayer);
        }
    }
    
    showStatus(message, type = 'info') {
        this.statusIndicator.className = `alert alert-${type} mt-2`;
        this.statusIndicator.textContent = message;
        this.statusIndicator.classList.remove('d-none');
    }
    
    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    async initializeButtons() {
        this.startButton.addEventListener('click', () => this.startRecording());
        this.stopButton.addEventListener('click', () => this.stopRecording());
    }
    
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => this.handleRecordingComplete();
            this.mediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event.error);
                this.showStatus('Error during recording. Please try again.', 'danger');
            };
            
            this.mediaRecorder.start();
            this.audioChunks = [];
            this.isRecording = true;
            this.startButton.disabled = true;
            this.stopButton.disabled = false;
            
            // Start recording timer
            this.recordingTime = 0;
            this.recordingTimer = setInterval(() => {
                this.recordingTime++;
                this.showStatus(`Recording in progress... ${this.formatTime(this.recordingTime)}`, 'info');
            }, 1000);
            
        } catch (err) {
            console.error('Error accessing microphone:', err);
            this.showStatus('Error accessing microphone. Please ensure microphone permissions are granted.', 'danger');
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            if (this.recordingTimer) {
                clearInterval(this.recordingTimer);
                this.recordingTimer = null;
            }
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.startButton.disabled = false;
            this.stopButton.disabled = true;
            this.showStatus('Processing recording...', 'info');
        }
    }
    
    async handleRecordingComplete() {
        try {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            this.audioPlayer.src = audioUrl;
            
            const urlParams = new URLSearchParams(window.location.search);
            const docId = urlParams.get('id');
            
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');
            formData.append('document_id', docId);
            
            this.showStatus('Uploading recording...', 'info');
            
            const response = await fetch('/api/upload-audio', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Upload failed');
            }
            
            console.log('Upload successful:', result.filename);
            this.showStatus('Recording uploaded successfully!', 'success');
            
            if (result.transcription) {
                this.transcriptionDisplay.textContent = result.transcription;
                const docResponse = await fetch('/api/generate-documentation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ document_id: docId })
                });
                
                if (!docResponse.ok) {
                    throw new Error('Failed to generate documentation');
                }
                
                window.location.reload();
            }
        } catch (err) {
            console.error('Error uploading audio:', err);
            this.showStatus(`Error: ${err.message}. Please try again.`, 'danger');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const recorder = new AudioRecorder();
    const docId = new URLSearchParams(window.location.search).get('id');
    if (docId) {
        fetch(`/api/audio/${docId}`)
            .then(response => {
                if (response.ok) {
                    return response.blob();
                }
            })
            .then(blob => {
                if (blob) {
                    const audioUrl = URL.createObjectURL(blob);
                    document.getElementById('audioPlayer').src = audioUrl;
                }
            })
            .catch(console.error);
    }
});

class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        
        this.startButton = document.getElementById('startRecording');
        this.stopButton = document.getElementById('stopRecording');
        this.audioPlayer = document.getElementById('audioPlayer');
        this.transcriptionDisplay = document.getElementById('transcriptionDisplay');
        
        this.initializeButtons();
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
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = () => this.handleRecordingComplete();
            
            this.mediaRecorder.start();
            this.isRecording = true;
            this.startButton.disabled = true;
            this.stopButton.disabled = false;
        } catch (err) {
            console.error('Error accessing microphone:', err);
            alert('Error accessing microphone. Please ensure microphone permissions are granted.');
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.startButton.disabled = false;
            this.stopButton.disabled = true;
        }
    }
    
    async handleRecordingComplete() {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        this.audioPlayer.src = audioUrl;
        
        // Get the current document ID from the URL
        const urlParams = new URLSearchParams(window.location.search);
        const docId = urlParams.get('id');
        
        // Upload the recording
        const formData = new FormData();
        formData.append('audio', audioBlob);
        formData.append('document_id', docId);
        
        try {
            const response = await fetch('/api/upload-audio', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Upload failed');
            }
            
            const result = await response.json();
            console.log('Upload successful:', result.filename);
            
            if (result.transcription) {
                this.transcriptionDisplay.textContent = result.transcription;
                // Generate documentation from transcription
                await fetch('/api/generate-documentation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ document_id: docId })
                });
                
                // Reload the page to show updated documentation
                window.location.reload();
            }
        } catch (err) {
            console.error('Error uploading audio:', err);
            alert('Error uploading recording. Please try again.');
        }
        
        this.audioChunks = [];
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const recorder = new AudioRecorder();
});

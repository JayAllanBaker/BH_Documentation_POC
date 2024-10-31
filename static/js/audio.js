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
            parentNode.insertBefore(this.statusIndicator, this.audioPlayer);
        }
    }
    
    showStatus(message, type = 'info') {
        this.statusIndicator.className = `alert alert-${type} mt-2`;
        this.statusIndicator.textContent = message;
        this.statusIndicator.classList.remove('d-none');
        
        if (type !== 'danger') {
            setTimeout(() => {
                this.statusIndicator.classList.add('d-none');
            }, 3000);
        }
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
            console.log('Starting recording process');
            this.showStatus('Requesting microphone access...', 'info');
            
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => this.handleRecordingComplete().catch(error => {
                console.error('Error in handleRecordingComplete:', error);
                this.showStatus('Error processing recording: ' + error.message, 'danger');
            });
            
            this.mediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event.error);
                this.showStatus('Error during recording: ' + event.error.message, 'danger');
                this.resetRecordingState();
            };
            
            this.mediaRecorder.start();
            this.audioChunks = [];
            this.isRecording = true;
            this.startButton.disabled = true;
            this.stopButton.disabled = false;
            
            this.recordingTime = 0;
            this.recordingTimer = setInterval(() => {
                this.recordingTime++;
                this.showStatus(`Recording in progress... ${this.formatTime(this.recordingTime)}`, 'info');
            }, 1000);
            
            console.log('Recording started successfully');
        } catch (err) {
            console.error('Error accessing microphone:', err);
            this.showStatus('Error accessing microphone: ' + err.message, 'danger');
            this.resetRecordingState();
        }
    }
    
    resetRecordingState() {
        this.isRecording = false;
        this.startButton.disabled = false;
        this.stopButton.disabled = true;
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            console.log('Stopping recording');
            if (this.recordingTimer) {
                clearInterval(this.recordingTimer);
                this.recordingTimer = null;
            }
            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            this.isRecording = false;
            this.startButton.disabled = false;
            this.stopButton.disabled = true;
            this.showStatus('Processing recording...', 'info');
        }
    }
    
    async handleRecordingComplete() {
        try {
            console.log('Starting recording upload process');
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            this.audioPlayer.src = audioUrl;
            
            // Get document ID from URL path instead of search params
            const docId = window.location.pathname.split('/')[2];
            console.log('Document ID from path:', docId);
            
            if (!docId || docId === '0') {
                this.showStatus('Please save the document before recording audio. Click the Save Document button first.', 'warning');
                return;
            }
            
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');
            formData.append('document_id', docId);
            
            this.showStatus('Uploading recording...', 'info');
            
            const response = await fetch('/api/upload-audio', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const result = await response.json().catch(() => ({ error: 'Network response was not ok' }));
                throw new Error(result.error || `HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Upload successful:', result);
            
            if (result.transcription) {
                this.transcriptionDisplay.textContent = result.transcription;
                console.log('Transcription received:', result.transcription);
                
                this.showStatus('Analyzing transcription for MEAT/TAMPER documentation...', 'info');
                
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
                
                const analysisResult = await docResponse.json();
                if (analysisResult.success) {
                    this.showStatus('MEAT/TAMPER analysis complete! Updating fields...', 'success');
                    
                    // Update all MEAT/TAMPER fields with the analysis results
                    for (const [key, value] of Object.entries(analysisResult.analysis)) {
                        const field = document.getElementById(key);
                        if (field) {
                            field.value = value;
                        }
                    }
                    
                    setTimeout(() => {
                        this.showStatus('Document updated successfully!', 'success');
                    }, 2000);
                } else {
                    throw new Error('Analysis failed');
                }
            }
        } catch (err) {
            console.error('Error:', err);
            this.showStatus(`Error: ${err.message}`, 'danger');
            throw err; // Re-throw to trigger the error handler in startRecording
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const recorder = new AudioRecorder();
    const docId = window.location.pathname.split('/')[2];
    
    if (docId && docId !== '0') {
        fetch(`/api/audio/${docId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch audio');
                }
                return response.blob();
            })
            .then(blob => {
                if (blob) {
                    const audioUrl = URL.createObjectURL(blob);
                    document.getElementById('audioPlayer').src = audioUrl;
                }
            })
            .catch(error => {
                console.error('Error fetching audio:', error);
                recorder.showStatus('Error loading previous recording', 'warning');
            });
    }
});

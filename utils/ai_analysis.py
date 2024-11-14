import os
import openai
import json
import logging
from typing import Dict, Any
import docx
import wave
import contextlib
import speech_recognition as sr
from pydub import AudioSegment
from flask import current_app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_document(file_path: str) -> str:
    """Extract text content from various document formats"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext in ['.wav', '.mp3']:
        return extract_text_from_audio(file_path)
    elif file_ext == '.docx':
        return extract_text_from_docx(file_path)
    elif file_ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif file_ext == '.pdf':
        # For now, return empty string for PDF
        # TODO: Implement PDF text extraction
        return ""
    return ""

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        return ""

def extract_text_from_audio(file_path: str) -> str:
    """Extract text from audio file using speech recognition"""
    try:
        # Convert MP3 to WAV if needed
        if file_path.lower().endswith('.mp3'):
            audio = AudioSegment.from_mp3(file_path)
            wav_path = file_path.rsplit('.', 1)[0] + '.wav'
            audio.export(wav_path, format='wav')
            file_path = wav_path

        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
            return recognizer.recognize_google(audio)
    except Exception as e:
        logger.error(f"Error extracting text from audio: {str(e)}")
        return ""

def extract_prapare_data(text: str) -> Dict[int, str]:
    """Extract PRAPARE assessment data from text"""
    try:
        client = openai.OpenAI()
        
        system_prompt = """You are a medical assessment analyzer specializing in PRAPARE assessments. 
        The Protocol for Responding to and Assessing Patient Assets, Risks, and Experiences (PRAPARE) 
        is a national effort to help health centers collect and apply data on social determinants 
        of health. Analyze the given text and extract relevant information for each PRAPARE question."""

        user_prompt = f"""Given this medical document, extract responses for PRAPARE assessment questions.
        Focus on social determinants of health including:
        - Hispanic/Latino status
        - Race
        - Seasonal/migrant work history
        - Veteran status
        - Preferred language
        - Family size
        - Housing situation
        - Education level
        - Employment status
        - Insurance status
        - Income level relative to poverty guidelines

        Document text:
        {text}

        Return the responses in a JSON format where keys are question IDs (1-13) and values are 
        the appropriate response values based on the PRAPARE assessment options."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        content = response.choices[0].message.content
        if isinstance(content, str):
            result = json.loads(content)
            return {int(k): v for k, v in result.items()}
        return {}
    except Exception as e:
        logger.error(f"Error in PRAPARE data extraction: {str(e)}")
        return {}

def extract_assessment_data(filepath: str, tool_type: str) -> Dict[int, str]:
    """Extract assessment data from document based on tool type"""
    try:
        # Get transcription from audio or text content from document
        text_content = extract_text_from_document(filepath)
        if not text_content:
            raise ValueError("No text content could be extracted from the document")

        # Create document record
        document = {
            'title': os.path.basename(filepath),
            'content': text_content,
            'transcription': text_content if filepath.lower().endswith(('.wav', '.mp3')) else None
        }

        # Extract responses based on tool type
        if tool_type.upper() == 'PRAPARE':
            responses = extract_prapare_data(text_content)
        else:
            # Default extraction for other assessment types
            responses = {}

        return responses
    except Exception as e:
        logger.error(f'Error in assessment data extraction: {str(e)}')
        raise

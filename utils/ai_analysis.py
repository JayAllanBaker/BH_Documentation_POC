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

def extract_assessment_data(file_path: str, assessment_tool: Any) -> Dict[int, str]:
    """
    Extract assessment data from document and map to assessment tool questions
    Returns a dictionary mapping question IDs to response values
    """
    try:
        # Extract text content from document
        text_content = extract_text_from_document(file_path)
        if not text_content:
            logger.error("No text content extracted from document")
            return {}

        # Prepare the prompt for analysis
        questions_prompt = "\n".join([
            f"Q{q.id}: {q.question_text}" 
            for q in assessment_tool.questions
        ])

        system_prompt = """You are a medical assessment analyzer. Given a medical document and a set of assessment questions:
1. Analyze the text for relevant information
2. Map the information to the specific assessment questions
3. For each question, provide the most appropriate response value based on the content
4. If a question cannot be answered from the content, skip it"""

        user_prompt = f"""Please analyze this medical document and provide responses for the following assessment questions:

Document Content:
{text_content}

Assessment Questions:
{questions_prompt}

For each question, provide only the response value that best matches the options available for that question. Format your response as a JSON object where keys are question IDs (Q1, Q2, etc.) and values are the response values."""

        # Get AI analysis
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0.3
        )

        # Process the response
        content = response.choices[0].message.content
        if isinstance(content, str):
            try:
                result = json.loads(content)
                # Convert response to proper format
                formatted_result = {}
                for q_id, value in result.items():
                    if q_id.startswith('Q'):
                        question_id = int(q_id[1:])  # Remove 'Q' prefix
                        formatted_result[question_id] = value
                return formatted_result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response: {e}")
                return {}
        return {}
    except Exception as e:
        logger.error(f"Error in assessment data extraction: {str(e)}")
        return {}

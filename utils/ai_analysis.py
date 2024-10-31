import os
import openai
import json
import logging
from typing import Dict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_transcription(transcription: str) -> Dict:
    """
    Analyze medical transcription using OpenAI GPT to categorize content according to MEAT/TAMPER standards.
    """
    client = openai.OpenAI()
    
    system_prompt = '''You are a medical documentation analyst specializing in MEAT and TAMPER standards. For each section:

MEAT:
- Monitor: Extract information about vital signs, symptoms, or ongoing condition monitoring (e.g., "PHQ9 score of 8.2, vital signs stable")
- Evaluate: Extract information about tests, examinations, or assessments performed (e.g., "Physical examination completed, PHQ9 assessment conducted")
- Assess: Extract information about diagnoses, interpretations of symptoms/tests (e.g., "Patient diagnosed with schizophrenia and mild depression")
- Treat: Extract information about medications, procedures, or treatment plans (e.g., "Prescribed Xanax for symptom management")

TAMPER:
- Time: Extract information about visit duration, time stamps, or scheduling (e.g., "Follow-up scheduled in seven days")
- Action: Extract information about what was done during the visit (e.g., "Conducted mental health assessment and medication review")
- Medical Necessity: Extract information justifying medical decisions (e.g., "Treatment required due to severe symptoms affecting daily functioning")
- Plan: Extract information about future treatment plans or follow-ups (e.g., "Will reassess medication efficacy in seven days")
- Education: Extract information about patient education or instructions (e.g., "Discussed medication side effects and coping strategies")
- Response: Extract information about patient's response to treatment (e.g., "Patient reports improved sleep with current medication")

Analyze the transcription and provide clear, concise text strings for each category.'''
    
    user_prompt = f"""Please analyze this medical transcription and categorize the content according to MEAT and TAMPER standards:

Transcription: {transcription}

For each category, provide only the relevant extracted information as a simple text string. Do not include any JSON structure in the extracted content. Format your response as JSON with these keys, where each value is a plain string:
- meat_monitor: a string containing vital signs, symptoms, or ongoing condition monitoring
- meat_evaluate: a string containing tests, examinations, or assessments performed
- meat_assess: a string containing diagnoses and interpretations
- meat_treat: a string containing medications, procedures, or treatment plans
- tamper_time: a string containing visit duration and scheduling info
- tamper_action: a string containing what was done during the visit
- tamper_medical_necessity: a string containing justification for medical decisions
- tamper_plan: a string containing future treatment plans
- tamper_education: a string containing patient education details
- tamper_response: a string containing patient's response to treatment"""

    try:
        logger.info("Sending request to OpenAI API")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0.3
        )
        
        logger.info("Received response from OpenAI")
        content = response.choices[0].message.content
        if isinstance(content, str):
            try:
                result = json.loads(content)
                logger.info("Successfully parsed OpenAI response")
                # Ensure all required fields exist and are strings
                required_fields = [
                    'meat_monitor', 'meat_evaluate', 'meat_assess', 'meat_treat',
                    'tamper_time', 'tamper_action', 'tamper_medical_necessity',
                    'tamper_plan', 'tamper_education', 'tamper_response'
                ]
                for field in required_fields:
                    if field not in result:
                        result[field] = ''
                    elif not isinstance(result[field], str):
                        result[field] = str(result[field])
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response: {e}")
                return {field: '' for field in required_fields}
        return content
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        required_fields = [
            'meat_monitor', 'meat_evaluate', 'meat_assess', 'meat_treat',
            'tamper_time', 'tamper_action', 'tamper_medical_necessity',
            'tamper_plan', 'tamper_education', 'tamper_response'
        ]
        return {field: '' for field in required_fields}

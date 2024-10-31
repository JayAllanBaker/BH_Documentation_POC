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
- Monitor: Extract information about vital signs, symptoms, or ongoing condition monitoring
- Evaluate: Extract information about tests, examinations, or assessments performed
- Assess: Extract information about diagnoses, interpretations of symptoms/tests
- Treat: Extract information about medications, procedures, or treatment plans

TAMPER:
- Time: Extract information about visit duration, time stamps, or scheduling
- Action: Extract information about what was done during the visit
- Medical Necessity: Extract information justifying medical decisions
- Plan: Extract information about future treatment plans or follow-ups
- Education: Extract information about patient education or instructions
- Response: Extract information about patient's response to treatment

Analyze the transcription and categorize all relevant information into these categories.'''
    
    user_prompt = f"""Please analyze this medical transcription and categorize the content according to MEAT and TAMPER standards:

    Transcription: {transcription}

    For each category, provide only the relevant extracted information. Format your response as JSON with these keys:
    - meat_monitor
    - meat_evaluate
    - meat_assess
    - meat_treat
    - tamper_time
    - tamper_action
    - tamper_medical_necessity
    - tamper_plan
    - tamper_education
    - tamper_response"""

    try:
        logger.info("Sending request to OpenAI API")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0.3  # Lower temperature for more consistent responses
        )
        
        try:
            content = response.choices[0].message.content
            if isinstance(content, str):
                logger.info("Successfully received and parsed OpenAI response")
                return json.loads(content)
            return content
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            return {}
            
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        return {}

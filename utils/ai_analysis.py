import os
import openai
from typing import Dict

openai.api_key = os.environ.get('OPENAI_API_KEY')

def analyze_transcription(transcription: str) -> Dict:
    """
    Analyze medical transcription using OpenAI GPT to categorize content according to MEAT/TAMPER standards.
    """
    system_prompt = """You are a medical documentation analyst. Your task is to analyze medical transcriptions and categorize the content according to MEAT (Monitor, Evaluate, Assess, Treat) and TAMPER (Time, Action, Medical Necessity, Plan, Education, Response) standards.
    
    For each category, extract relevant information from the transcription. If no information is found for a category, return an empty string."""
    
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            response_format={ "type": "json_object" }
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error in AI analysis: {str(e)}")
        return {}

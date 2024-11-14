from app import app  # Import the Flask app
from models import db, AssessmentTool, AssessmentQuestion
from datetime import datetime

def init_prapare_assessment():
    with app.app_context():  # Add application context
        # Create PRAPARE assessment tool
        prapare = AssessmentTool()
        prapare.name = "PRAPARE Assessment"
        prapare.description = "Protocol for Responding to and Assessing Patient Assets, Risks, and Experiences"
        prapare.version = "September 2, 2016"
        prapare.tool_type = "PRAPARE"
        prapare.active = True
        prapare.created_at = datetime.utcnow()
        prapare.updated_at = datetime.utcnow()
        
        db.session.add(prapare)
        db.session.flush()  # Get the ID
        
        # Personal Characteristics Questions (1-5)
        questions = [
            {
                "order": 1,
                "question_text": "Are you Hispanic or Latino?",
                "question_type": "multiple_choice",
                "options": [
                    {"value": "yes", "text": "Yes", "score": 0},
                    {"value": "no", "text": "No", "score": 0},
                    {"value": "no_answer", "text": "I choose not to answer this question", "score": 0}
                ],
                "required": True,
                "help_text": "Please select one option"
            },
            {
                "order": 2,
                "question_text": "Which race(s) are you? Check all that apply",
                "question_type": "multiple_choice",
                "options": [
                    {"value": "asian", "text": "Asian", "score": 0},
                    {"value": "pacific_islander", "text": "Pacific Islander", "score": 0},
                    {"value": "white", "text": "White", "score": 0},
                    {"value": "black", "text": "Black/African American", "score": 0},
                    {"value": "native", "text": "American Indian/Alaskan Native", "score": 0},
                    {"value": "other", "text": "Other (please write)", "score": 0},
                    {"value": "no_answer", "text": "I choose not to answer this question", "score": 0}
                ],
                "required": False,  # Changed to False as requested
                "help_text": "You may select multiple options"
            },
            {
                "order": 3,
                "question_text": "At any point in the past 2 years, has season or migrant farm work been your or your family's main source of income?",
                "question_type": "multiple_choice",
                "options": [
                    {"value": "yes", "text": "Yes", "score": 1},
                    {"value": "no", "text": "No", "score": 0},
                    {"value": "no_answer", "text": "I choose not to answer this question", "score": 0}
                ],
                "required": True,
                "help_text": "This helps us understand your work situation"
            },
            {
                "order": 4,
                "question_text": "Have you been discharged from the armed forces of the United States?",
                "question_type": "multiple_choice",
                "options": [
                    {"value": "yes", "text": "Yes", "score": 1},
                    {"value": "no", "text": "No", "score": 0},
                    {"value": "no_answer", "text": "I choose not to answer this question", "score": 0}
                ],
                "required": True,
                "help_text": "This information helps us connect you with veteran services if applicable"
            },
            {
                "order": 5,
                "question_text": "What language are you most comfortable speaking?",
                "question_type": "text",
                "required": True,
                "help_text": "Please specify your preferred language"
            },
            # Family & Home Questions (6-8)
            {
                "order": 6,
                "question_text": "How many family members, including yourself, do you currently live with?",
                "question_type": "number",
                "required": True,
                "help_text": "Enter the total number of family members in your household"
            },
            {
                "order": 7,
                "question_text": "What is your housing situation today?",
                "question_type": "multiple_choice",
                "options": [
                    {"value": "have_housing", "text": "I have housing", "score": 0},
                    {"value": "no_housing", "text": "I do not have housing (staying with others, in a hotel, in a shelter, living outside on the street, on a beach, in a car, or in a park)", "score": 1},
                    {"value": "no_answer", "text": "I choose not to answer this question", "score": 0}
                ],
                "required": True,
                "help_text": "Select the option that best describes your current housing situation"
            },
            {
                "order": 8,
                "question_text": "Are you worried about losing your housing?",
                "question_type": "multiple_choice",
                "options": [
                    {"value": "yes", "text": "Yes", "score": 1},
                    {"value": "no", "text": "No", "score": 0},
                    {"value": "no_answer", "text": "I choose not to answer this question", "score": 0}
                ],
                "required": True,
                "help_text": "This helps us understand your housing security concerns"
            },
            # Money & Resources Questions (9-13)
            {
                "order": 9,
                "question_text": "What address do you live at?",
                "question_type": "text",
                "required": False,  # Changed from True to False
                "help_text": "Please provide your full address including Street, City, State, and Zip code"
            },
            {
                "order": 10,
                "question_text": "What is the highest level of school that you have finished?",
                "question_type": "multiple_choice",
                "options": [
                    {"value": "less_than_high_school", "text": "Less than high school degree", "score": 1},
                    {"value": "high_school", "text": "High school diploma or GED", "score": 0},
                    {"value": "more_than_high_school", "text": "More than high school", "score": 0},
                    {"value": "no_answer", "text": "I choose not to answer this question", "score": 0}
                ],
                "required": True,
                "help_text": "Select your highest completed education level"
            },
            {
                "order": 11,
                "question_text": "What is your current work situation?",
                "question_type": "multiple_choice",
                "options": [
                    {"value": "unemployed", "text": "Unemployed", "score": 1},
                    {"value": "part_time", "text": "Part-time or temporary work", "score": 0.5},
                    {"value": "full_time", "text": "Full-time work", "score": 0},
                    {"value": "otherwise_unemployed", "text": "Otherwise unemployed but not seeking work (ex: student, retired, disabled, unpaid primary care giver)", "score": 0},
                    {"value": "no_answer", "text": "I choose not to answer this question", "score": 0}
                ],
                "required": True,
                "help_text": "Select the option that best describes your current employment status"
            },
            {
                "order": 12,
                "question_text": "What is your main insurance?",
                "question_type": "multiple_choice",
                "options": [
                    {"value": "none", "text": "None/uninsured", "score": 1},
                    {"value": "medicaid", "text": "Medicaid", "score": 0},
                    {"value": "chip", "text": "CHIP Medicaid", "score": 0},
                    {"value": "medicare", "text": "Medicare", "score": 0},
                    {"value": "other_public", "text": "Other public insurance (not CHIP)", "score": 0},
                    {"value": "private", "text": "Private Insurance", "score": 0},
                    {"value": "no_answer", "text": "I choose not to answer this question", "score": 0}
                ],
                "required": True,
                "help_text": "Select your primary insurance coverage"
            },
            {
                "order": 13,
                "question_text": "During the past year, what was the total combined income for you and the family members you live with? This information will help us determine if you are eligible for any benefits.",
                "question_type": "multiple_choice",
                "options": [
                    {"value": "below_poverty", "text": "Below federal poverty level", "score": 1},
                    {"value": "above_poverty", "text": "Above federal poverty level", "score": 0},
                    {"value": "no_answer", "text": "I choose not to answer this question", "score": 0}
                ],
                "required": True,
                "help_text": "This information is used to determine eligibility for various assistance programs"
            }
        ]
        
        # Add all questions
        for q in questions:
            question = AssessmentQuestion()
            question.tool_id = prapare.id
            question.question_text = q["question_text"]
            question.order = q["order"]
            question.question_type = q["question_type"]
            question.required = q["required"]
            question.help_text = q.get("help_text")
            question.options = q.get("options")
            question.created_at = datetime.utcnow()
            question.updated_at = datetime.utcnow()
            db.session.add(question)
        
        try:
            db.session.commit()
            print("PRAPARE assessment tool created successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating PRAPARE assessment: {str(e)}")
            raise

def init_cows_assessment():
    with app.app_context():
        # Create COWS assessment tool
        cows = AssessmentTool()
        cows.name = "Clinical Opiate Withdrawal Scale (COWS)"
        cows.description = "The Clinical Opiate Withdrawal Scale (COWS) is used to assess and monitor withdrawal symptoms in patients with opioid dependence."
        cows.version = "1.0"
        cows.tool_type = "COWS"
        cows.active = True
        cows.scoring_logic = {
            "ranges": [
                {"min": 0, "max": 5, "severity": "Mild withdrawal"},
                {"min": 5, "max": 12, "severity": "Moderate withdrawal"},
                {"min": 13, "max": 24, "severity": "Moderately severe withdrawal"},
                {"min": 25, "max": 36, "severity": "Severe withdrawal"},
                {"min": 37, "max": float('inf'), "severity": "Very severe withdrawal"}
            ]
        }
        cows.created_at = datetime.utcnow()
        cows.updated_at = datetime.utcnow()
        
        db.session.add(cows)
        db.session.flush()
        
        # COWS Questions with proper scoring
        questions = [
            {
                "order": 1,
                "question_text": "Resting Pulse Rate (beats/minute)",
                "question_type": "scale",
                "options": [
                    {"value": "0", "text": "80 or below", "score": 0},
                    {"value": "1", "text": "81-100", "score": 1},
                    {"value": "2", "text": "101-120", "score": 2},
                    {"value": "4", "text": "Greater than 120", "score": 4}
                ],
                "required": True,
                "help_text": "Measure after patient is sitting/lying for one minute"
            },
            {
                "order": 2,
                "question_text": "Sweating",
                "question_type": "scale",
                "options": [
                    {"value": "0", "text": "No report of chills or flushing", "score": 0},
                    {"value": "1", "text": "Subjective report of chills or flushing", "score": 1},
                    {"value": "2", "text": "Flushed or observable moistness on face", "score": 2},
                    {"value": "3", "text": "Beads of sweat on brow or face", "score": 3},
                    {"value": "4", "text": "Sweat streaming off face", "score": 4}
                ],
                "required": True,
                "help_text": "Over past 30 minutes"
            },
            {
                "order": 3,
                "question_text": "Restlessness",
                "question_type": "scale",
                "options": [
                    {"value": "0", "text": "Able to sit still", "score": 0},
                    {"value": "1", "text": "Reports difficulty sitting still, but is able to do so", "score": 1},
                    {"value": "3", "text": "Frequent shifting or extraneous movements of legs/arms", "score": 3},
                    {"value": "5", "text": "Unable to sit still for more than a few seconds", "score": 5}
                ],
                "required": True,
                "help_text": "Observation during assessment"
            },
            {
                "order": 4,
                "question_text": "Pupil Size",
                "question_type": "scale",
                "options": [
                    {"value": "0", "text": "Pupils pinned or normal size for room light", "score": 0},
                    {"value": "1", "text": "Pupils possibly larger than normal for room light", "score": 1},
                    {"value": "2", "text": "Pupils moderately dilated", "score": 2},
                    {"value": "5", "text": "Pupils so dilated that only rim of iris is visible", "score": 5}
                ],
                "required": True,
                "help_text": "Observe in normal room light"
            },
            {
                "order": 5,
                "question_text": "Bone or Joint Aches",
                "question_type": "scale",
                "options": [
                    {"value": "0", "text": "Not present", "score": 0},
                    {"value": "1", "text": "Mild diffuse discomfort", "score": 1},
                    {"value": "2", "text": "Patient reports severe diffuse aching of joints/muscles", "score": 2},
                    {"value": "4", "text": "Patient is rubbing joints or muscles plus unable to sit still", "score": 4}
                ],
                "required": True,
                "help_text": "If patient was having pain previously, only the additional component attributed to opioid withdrawal is scored"
            },
            {
                "order": 6,
                "question_text": "Runny Nose or Tearing",
                "question_type": "scale",
                "options": [
                    {"value": "0", "text": "Not present", "score": 0},
                    {"value": "1", "text": "Nasal stuffiness or unusually moist eyes", "score": 1},
                    {"value": "2", "text": "Nose running or tearing", "score": 2},
                    {"value": "4", "text": "Nose constantly running or tears streaming down cheeks", "score": 4}
                ],
                "required": True,
                "help_text": "Not accounted for by cold symptoms or allergies"
            },
            {
                "order": 7,
                "question_text": "GI Upset",
                "question_type": "scale",
                "options": [
                    {"value": "0", "text": "No GI symptoms", "score": 0},
                    {"value": "1", "text": "Stomach cramps", "score": 1},
                    {"value": "2", "text": "Nausea or loose stool", "score": 2},
                    {"value": "3", "text": "Vomiting or diarrhea", "score": 3},
                    {"value": "5", "text": "Multiple episodes of diarrhea or vomiting", "score": 5}
                ],
                "required": True,
                "help_text": "Over last 30 minutes"
            },
            {
                "order": 8,
                "question_text": "Tremor",
                "question_type": "scale",
                "options": [
                    {"value": "0", "text": "No tremor", "score": 0},
                    {"value": "1", "text": "Tremor can be felt, but not observed", "score": 1},
                    {"value": "2", "text": "Slight tremor observable", "score": 2},
                    {"value": "4", "text": "Gross tremor or muscle twitching", "score": 4}
                ],
                "required": True,
                "help_text": "Observation of outstretched hands"
            },
            {
                "order": 9,
                "question_text": "Yawning",
                "question_type": "scale",
                "options": [
                    {"value": "0", "text": "No yawning", "score": 0},
                    {"value": "1", "text": "Yawning once or twice during assessment", "score": 1},
                    {"value": "2", "text": "Yawning three or more times during assessment", "score": 2},
                    {"value": "4", "text": "Yawning several times/minute", "score": 4}
                ],
                "required": True,
                "help_text": "Observation during assessment"
            },
            {
                "order": 10,
                "question_text": "Anxiety or Irritability",
                "question_type": "scale",
                "options": [
                    {"value": "0", "text": "None", "score": 0},
                    {"value": "1", "text": "Patient reports increasing irritability or anxiousness", "score": 1},
                    {"value": "2", "text": "Patient obviously irritable or anxious", "score": 2},
                    {"value": "4", "text": "Patient so irritable or anxious that participation in the assessment is difficult", "score": 4}
                ],
                "required": True,
                "help_text": "Observation during assessment"
            },
            {
                "order": 11,
                "question_text": "Gooseflesh Skin",
                "question_type": "scale",
                "options": [
                    {"value": "0", "text": "Skin is smooth", "score": 0},
                    {"value": "3", "text": "Piloerrection of skin can be felt or hairs standing up on arms", "score": 3},
                    {"value": "5", "text": "Prominent piloerrection", "score": 5}
                ],
                "required": True,
                "help_text": "Observe skin on outer arm"
            }
        ]
        
        # Add all COWS questions
        for q in questions:
            question = AssessmentQuestion()
            question.tool_id = cows.id
            question.question_text = q["question_text"]
            question.order = q["order"]
            question.question_type = q["question_type"]
            question.required = q["required"]
            question.help_text = q.get("help_text")
            question.options = q.get("options")
            question.created_at = datetime.utcnow()
            question.updated_at = datetime.utcnow()
            db.session.add(question)
        
        try:
            db.session.commit()
            print("COWS assessment tool created successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating COWS assessment: {str(e)}")
            raise

if __name__ == "__main__":
    # Clean up existing assessment tools first
    with app.app_context():
        AssessmentResponse.query.delete()
        AssessmentResult.query.delete()
        AssessmentQuestion.query.delete()
        AssessmentTool.query.delete()
        db.session.commit()
    
    # Initialize both assessment tools
    init_prapare_assessment()
    init_cows_assessment()
from app import app  # Import the Flask app
from models import db, AssessmentTool, AssessmentQuestion
from datetime import datetime

def init_prapare_assessment():
    with app.app_context():  # Add application context
        # Create PRAPARE assessment tool
        prapare = AssessmentTool(
            name="PRAPARE Assessment",
            description="Protocol for Responding to and Assessing Patient Assets, Risks, and Experiences",
            version="September 2, 2016",
            tool_type="PRAPARE",
            active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
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
                "required": True,
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
                "required": True,
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
            question = AssessmentQuestion(
                tool_id=prapare.id,
                question_text=q["question_text"],
                order=q["order"],
                question_type=q["question_type"],
                required=q["required"],
                help_text=q.get("help_text"),
                options=q.get("options"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(question)
        
        try:
            db.session.commit()
            print("PRAPARE assessment tool created successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating PRAPARE assessment: {str(e)}")
            raise

if __name__ == "__main__":
    init_prapare_assessment()

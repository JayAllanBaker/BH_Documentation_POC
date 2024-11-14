from models import db, AssessmentTool, AssessmentQuestion
from datetime import datetime

def init_prapare_assessment():
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
                {"value": "yes", "text": "Yes"},
                {"value": "no", "text": "No"},
                {"value": "no_answer", "text": "I choose not to answer this question"}
            ],
            "required": True
        },
        {
            "order": 2,
            "question_text": "Which race(s) are you? Check all that apply",
            "question_type": "multiple_choice",
            "options": [
                {"value": "asian", "text": "Asian"},
                {"value": "pacific_islander", "text": "Pacific Islander"},
                {"value": "white", "text": "White"},
                {"value": "black", "text": "Black/African American"},
                {"value": "native", "text": "American Indian/Alaskan Native"},
                {"value": "other", "text": "Other"},
                {"value": "no_answer", "text": "I choose not to answer this question"}
            ],
            "required": True
        },
        {
            "order": 3,
            "question_text": "At any point in the past 2 years, has season or migrant farm work been your or your family's main source of income?",
            "question_type": "multiple_choice",
            "options": [
                {"value": "yes", "text": "Yes"},
                {"value": "no", "text": "No"},
                {"value": "no_answer", "text": "I choose not to answer this question"}
            ],
            "required": True
        },
        {
            "order": 4,
            "question_text": "Have you been discharged from the armed forces of the United States?",
            "question_type": "multiple_choice",
            "options": [
                {"value": "yes", "text": "Yes"},
                {"value": "no", "text": "No"},
                {"value": "no_answer", "text": "I choose not to answer this question"}
            ],
            "required": True
        },
        {
            "order": 5,
            "question_text": "What language are you most comfortable speaking?",
            "question_type": "text",
            "required": True
        },
        # Family & Home Questions (6-8)
        {
            "order": 6,
            "question_text": "How many family members, including yourself, do you currently live with?",
            "question_type": "number",
            "required": True,
            "help_text": "Enter the number of family members"
        },
        {
            "order": 7,
            "question_text": "What is your housing situation today?",
            "question_type": "multiple_choice",
            "options": [
                {"value": "have_housing", "text": "I have housing"},
                {"value": "no_housing", "text": "I do not have housing (staying with others, in a hotel, in a shelter, living outside on the street, on a beach, in a car, or in a park)"},
                {"value": "no_answer", "text": "I choose not to answer this question"}
            ],
            "required": True
        },
        {
            "order": 8,
            "question_text": "Are you worried about losing your housing?",
            "question_type": "multiple_choice",
            "options": [
                {"value": "yes", "text": "Yes"},
                {"value": "no", "text": "No"},
                {"value": "no_answer", "text": "I choose not to answer this question"}
            ],
            "required": True
        },
        # Money & Resources Questions (9-13)
        {
            "order": 9,
            "question_text": "What address do you live at?",
            "question_type": "text",
            "required": True,
            "help_text": "Include Street, City, State, Zip code"
        },
        {
            "order": 10,
            "question_text": "What is the highest level of school that you have finished?",
            "question_type": "multiple_choice",
            "options": [
                {"value": "less_than_high_school", "text": "Less than high school degree"},
                {"value": "high_school", "text": "High school diploma or GED"},
                {"value": "more_than_high_school", "text": "More than high school"},
                {"value": "no_answer", "text": "I choose not to answer this question"}
            ],
            "required": True
        },
        {
            "order": 11,
            "question_text": "What is your current work situation?",
            "question_type": "multiple_choice",
            "options": [
                {"value": "unemployed", "text": "Unemployed"},
                {"value": "part_time", "text": "Part-time or temporary work"},
                {"value": "full_time", "text": "Full-time work"},
                {"value": "otherwise_unemployed", "text": "Otherwise unemployed but not seeking work"},
                {"value": "no_answer", "text": "I choose not to answer this question"}
            ],
            "required": True
        },
        {
            "order": 12,
            "question_text": "What is your main insurance?",
            "question_type": "multiple_choice",
            "options": [
                {"value": "none", "text": "None/uninsured"},
                {"value": "medicaid", "text": "Medicaid"},
                {"value": "chip", "text": "CHIP Medicaid"},
                {"value": "medicare", "text": "Medicare"},
                {"value": "other_public", "text": "Other public insurance (not CHIP)"},
                {"value": "private", "text": "Private Insurance"},
                {"value": "no_answer", "text": "I choose not to answer this question"}
            ],
            "required": True
        },
        {
            "order": 13,
            "question_text": "During the past year, what was the total combined income for you and the family members you live with? This information will help us determine if you are eligible for any benefits.",
            "question_type": "text",
            "required": True,
            "help_text": "Include income from all sources"
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

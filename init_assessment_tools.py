from app import app, db
from models import AssessmentTool, AssessmentQuestion
from utils.cows_config import COWS_TOOL

def init_cows_assessment():
    """Initialize the COWS assessment tool in the database"""
    with app.app_context():
        # Check if COWS tool already exists
        existing_tool = AssessmentTool.query.filter_by(
            name=COWS_TOOL['name'],
            version=COWS_TOOL['version']
        ).first()
        
        if existing_tool:
            print(f"COWS tool version {COWS_TOOL['version']} already exists")
            return existing_tool
            
        # Create new COWS tool
        tool = AssessmentTool(
            name=COWS_TOOL['name'],
            description=COWS_TOOL['description'],
            version=COWS_TOOL['version'],
            tool_type=COWS_TOOL['tool_type'],
            scoring_logic=COWS_TOOL['scoring_logic'],
            active=True
        )
        
        db.session.add(tool)
        db.session.flush()  # Get the tool ID
        
        # Create questions
        for question_data in COWS_TOOL['questions']:
            question = AssessmentQuestion(
                tool_id=tool.id,
                question_text=question_data['question_text'],
                order=question_data['order'],
                question_type=question_data['question_type'],
                options=question_data['options'],
                required=question_data['required'],
                help_text=question_data['help_text']
            )
            db.session.add(question)
        
        db.session.commit()
        print(f"Successfully initialized COWS tool version {COWS_TOOL['version']}")
        return tool

if __name__ == '__main__':
    init_cows_assessment()

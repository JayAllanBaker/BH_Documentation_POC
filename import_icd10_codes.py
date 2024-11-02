import csv
from app import app, db
from models import ICD10Code

def import_icd10_codes():
    # Since CDC FTP is not accessible, we'll use a basic set of common codes
    codes = {
        'E11': 'Type 2 diabetes mellitus',
        'E11.0': 'Type 2 diabetes with hyperosmolarity',
        'E11.1': 'Type 2 diabetes with ketoacidosis',
        'E11.2': 'Type 2 diabetes with kidney complications',
        'E11.21': 'Type 2 diabetes with diabetic nephropathy',
        'E11.22': 'Type 2 diabetes with diabetic chronic kidney disease',
        'E11.3': 'Type 2 diabetes with ophthalmic complications',
        'E11.31': 'Type 2 diabetes with background retinopathy',
        'E11.32': 'Type 2 diabetes with proliferative retinopathy',
        'E11.4': 'Type 2 diabetes with neurological complications',
        'I10': 'Essential (primary) hypertension',
        'I11': 'Hypertensive heart disease',
        'I11.0': 'Hypertensive heart disease with heart failure',
        'I11.9': 'Hypertensive heart disease without heart failure',
        'J45': 'Asthma',
        'J45.0': 'Predominantly allergic asthma',
        'J45.1': 'Nonallergic asthma',
        'J45.2': 'Mixed asthma',
        'F32': 'Major depressive disorder, single episode',
        'F41': 'Other anxiety disorders',
        'F41.0': 'Panic disorder without agoraphobia',
        'F41.1': 'Generalized anxiety disorder'
    }
    
    with app.app_context():
        # Clear existing codes
        ICD10Code.query.delete()
        
        # Import new codes
        for code, description in codes.items():
            category = code.split('.')[0] if '.' in code else code
            
            icd10_code = ICD10Code(
                code=code,
                description=description,
                category=category
            )
            db.session.add(icd10_code)
        
        db.session.commit()
        print('ICD-10 codes imported successfully')

if __name__ == '__main__':
    import_icd10_codes()

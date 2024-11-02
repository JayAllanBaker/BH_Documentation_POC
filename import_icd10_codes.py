import csv
import requests
from app import app, db
from models import ICD10Code

def import_icd10_codes():
    # Download ICD-10 codes from CDC website
    url = 'https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2024/icd10cm_codes_2024.txt'
    response = requests.get(url)
    
    if response.status_code == 200:
        # Process the downloaded file
        lines = response.text.splitlines()
        reader = csv.reader(lines, delimiter='	')
        
        with app.app_context():
            # Clear existing codes
            ICD10Code.query.delete()
            
            # Import new codes
            for row in reader:
                if len(row) >= 2:
                    code = row[0].strip()
                    description = row[1].strip()
                    category = code.split('.')[0] if '.' in code else code
                    
                    icd10_code = ICD10Code(
                        code=code,
                        description=description,
                        category=category
                    )
                    db.session.add(icd10_code)
            
            db.session.commit()
            print('ICD-10 codes imported successfully')
    else:
        print('Failed to download ICD-10 codes')

if __name__ == '__main__':
    import_icd10_codes()

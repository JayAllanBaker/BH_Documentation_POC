from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from utils.search import search_patients, search_documents, get_code_suggestions
from models import ICD10Code

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    
    patients = []
    documents = []
    
    if search_type in ['all', 'patients']:
        patients = search_patients(query)
    if search_type in ['all', 'documents']:
        documents = search_documents(query)
        
    return render_template('search/results.html', 
                         query=query,
                         search_type=search_type,
                         patients=patients,
                         documents=documents)

@search_bp.route('/api/code-suggestions')
@login_required
def code_suggestions():
    query = request.args.get('q', '')
    suggestions = []
    
    # Get ICD-10 suggestions from database
    if query:
        icd10_codes = ICD10Code.search_codes(query)
        suggestions.extend([{
            'code': code.code,
            'description': code.description,
            'system': 'ICD-10'
        } for code in icd10_codes])
        
    # Add SNOMED CT suggestions (keep existing ones)
    snomed_suggestions = get_code_suggestions(query)
    suggestions.extend(snomed_suggestions)
    
    return jsonify(suggestions)

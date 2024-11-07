from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from utils.search import search_patients, search_documents, get_code_suggestions
from models import ICD10Code
from utils.audit import audit_log
from functools import wraps
import re

search_bp = Blueprint('search', __name__)

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f'Error in {f.__name__}: {str(e)}')
            return jsonify({'error': 'An unexpected error occurred'}), 500
    return decorated_function

def sanitize_query(query):
    # Remove dangerous characters and SQL injection attempts
    sanitized = re.sub(r'[;\'"\[\]\\]', '', query)
    # Limit query length
    return sanitized[:500] if sanitized else ''

@search_bp.route('/search', methods=['GET'])
@login_required
@audit_log(action='search', resource_type='global')
@handle_errors
def search():
    query = sanitize_query(request.args.get('q', ''))
    search_type = request.args.get('type', 'all')
    
    if search_type not in ['all', 'patients', 'documents']:
        search_type = 'all'
    
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
@audit_log(action='code_search', resource_type='icd10')
@handle_errors
def code_suggestions():
    query = sanitize_query(request.args.get('q', ''))
    code_type = request.args.get('type', '').upper()
    suggestions = []
    
    try:
        if query:
            # Get ICD-10 suggestions from database
            if not code_type or code_type == 'ICD-10':
                icd10_codes = ICD10Code.search_codes(query)
                suggestions.extend([{
                    'code': code.code,
                    'description': code.description,
                    'system': 'ICD-10'
                } for code in icd10_codes])
            
            # Get SNOMED CT suggestions if requested
            if not code_type or code_type == 'SNOMED-CT':
                snomed_suggestions = get_code_suggestions(query, 'SNOMED-CT')
                suggestions.extend(snomed_suggestions)
            
            # Sort and limit results
            suggestions.sort(key=lambda x: (
                0 if x['code'].startswith(query) else 1,
                len(x['code']),
                x['code']
            ))
            suggestions = suggestions[:10]
        
        return jsonify(suggestions)
    except Exception as e:
        current_app.logger.error(f'Error getting code suggestions: {str(e)}')
        return jsonify({'error': 'Error fetching suggestions'}), 500

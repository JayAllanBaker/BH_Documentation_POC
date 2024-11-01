from flask import Blueprint, render_template, request
from flask_login import login_required
from utils.search import search_patients, search_documents

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

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models import Document
import os

docs_bp = Blueprint('documentation', __name__)

@docs_bp.route('/documents')
@login_required
def list():
    documents = Document.query.filter_by(author_id=current_user.id).order_by(Document.created_at.desc()).all()
    return render_template('documentation/list.html', documents=documents)

@docs_bp.route('/documents/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    if id == 0:
        doc = Document(
            title='New Document',
            content='',
            author_id=current_user.id
        )
        db.session.add(doc)
        db.session.commit()
        return redirect(url_for('documentation.edit', id=doc.id))
        
    doc = Document.query.get_or_404(id)
    if doc.author_id != current_user.id:
        flash('You do not have permission to edit this document')
        return redirect(url_for('documentation.list'))
        
    if request.method == 'POST':
        doc.title = request.form['title']
        doc.content = request.form['content']
        # MEAT fields
        doc.meat_monitor = request.form['meat_monitor']
        doc.meat_evaluate = request.form['meat_evaluate']
        doc.meat_assess = request.form['meat_assess']
        doc.meat_treat = request.form['meat_treat']
        # TAMPER fields
        doc.tamper_time = request.form['tamper_time']
        doc.tamper_action = request.form['tamper_action']
        doc.tamper_medical_necessity = request.form['tamper_medical_necessity']
        doc.tamper_plan = request.form['tamper_plan']
        doc.tamper_education = request.form['tamper_education']
        doc.tamper_response = request.form['tamper_response']
        
        db.session.commit()
        flash('Document updated successfully')
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'id': doc.id})
        return redirect(url_for('documentation.edit', id=doc.id))
        
    return render_template('documentation/edit.html', doc=doc)

@docs_bp.route('/documents/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    doc = Document.query.get_or_404(id)
    
    if doc.author_id != current_user.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Unauthorized access'}), 403
        flash('You do not have permission to delete this document')
        return redirect(url_for('documentation.list'))
    
    try:
        # Delete associated audio file if it exists
        if doc.recording_path and os.path.exists(doc.recording_path):
            os.remove(doc.recording_path)
        
        # Delete the document from database
        db.session.delete(doc)
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
            
        flash('Document deleted successfully')
        return redirect(url_for('documentation.list'))
        
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': str(e)}), 500
            
        flash(f'Error deleting document: {str(e)}')
        return redirect(url_for('documentation.list'))

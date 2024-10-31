from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models import Document
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        try:
            db.session.commit()
            flash('Document updated successfully')
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'id': doc.id})
            return redirect(url_for('documentation.edit', id=doc.id))
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Failed to update document'}), 500
            flash('Error updating document')
            return redirect(url_for('documentation.edit', id=doc.id))
        
    return render_template('documentation/edit.html', doc=doc)

@docs_bp.route('/documents/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    try:
        doc = Document.query.get_or_404(id)
        
        if doc.author_id != current_user.id:
            logger.warning(f"Unauthorized deletion attempt for document {id} by user {current_user.id}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'You do not have permission to delete this document'}), 403
            flash('You do not have permission to delete this document')
            return redirect(url_for('documentation.list'))
        
        # Delete associated audio file if it exists
        if doc.recording_path:
            try:
                if os.path.exists(doc.recording_path):
                    os.remove(doc.recording_path)
            except OSError as e:
                logger.error(f"Error deleting audio file: {str(e)}")
                # Continue with document deletion even if audio file deletion fails
        
        # Delete the document from database
        db.session.delete(doc)
        db.session.commit()
        
        logger.info(f"Document {id} deleted successfully by user {current_user.id}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Document deleted successfully'
            })
            
        flash('Document deleted successfully')
        return redirect(url_for('documentation.list'))
        
    except Exception as e:
        logger.error(f"Error deleting document {id}: {str(e)}")
        db.session.rollback()
        
        error_message = 'An error occurred while deleting the document'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'error': error_message,
                'details': str(e)
            }), 500
            
        flash(error_message)
        return redirect(url_for('documentation.list'))

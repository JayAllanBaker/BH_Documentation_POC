from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models import Document, db
from datetime import datetime

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/documents')
@login_required
def list_documents():
    documents = Document.query.filter_by(user_id=current_user.id).all()
    return render_template('documents/list.html', documents=documents)

@documents_bp.route('/documents/new', methods=['GET', 'POST'])
@login_required
def create_document():
    if request.method == 'POST':
        title = request.form.get('title')
        document = Document(title=title, user_id=current_user.id)
        db.session.add(document)
        db.session.commit()
        return redirect(url_for('documents.edit_document', id=document.id))
    return render_template('documents/new.html')

@documents_bp.route('/documents/<int:id>')
@login_required
def view_document(id):
    document = Document.query.get_or_404(id)
    if document.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('documents.list_documents'))
    return render_template('documents/view.html', document=document)

@documents_bp.route('/documents/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_document(id):
    document = Document.query.get_or_404(id)
    if document.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('documents.list_documents'))
    
    if request.method == 'POST':
        document.title = request.form.get('title')
        document.content = request.form.get('content')
        document.updated_at = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('documents.view_document', id=id))
    
    return render_template('documents/edit.html', document=document)

@documents_bp.route('/documents/<int:id>/delete', methods=['POST'])
@login_required
def delete_document(id):
    document = Document.query.get_or_404(id)
    if document.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('documents.list_documents'))
    
    db.session.delete(document)
    db.session.commit()
    flash('Document deleted successfully')
    return redirect(url_for('documents.list_documents'))

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models import Document

docs_bp = Blueprint('documentation', __name__)

@docs_bp.route('/documents')
@login_required
def list():
    documents = Document.query.filter_by(author_id=current_user.id).order_by(Document.created_at.desc()).all()
    return render_template('documentation/list.html', documents=documents)

@docs_bp.route('/documents/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    doc = Document.query.get_or_404(id)
    if doc.author_id != current_user.id:
        flash('You do not have permission to edit this document')
        return redirect(url_for('documentation.list'))
        
    if request.method == 'POST':
        doc.title = request.form['title']
        doc.content = request.form['content']
        doc.meat_monitor = request.form['meat_monitor']
        doc.meat_evaluate = request.form['meat_evaluate']
        doc.meat_assess = request.form['meat_assess'] 
        doc.meat_treat = request.form['meat_treat']
        db.session.commit()
        flash('Document updated successfully')
        return redirect(url_for('documentation.list'))
        
    return render_template('documentation/edit.html', doc=doc)

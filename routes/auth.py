from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Both username and password are required')
                return render_template('auth/login.html')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                app.logger.info(f'Successful login for user: {username}')
                return redirect(url_for('main.dashboard'))
            
            app.logger.warning(f'Failed login attempt for username: {username}')
            flash('Invalid username or password')
            
        except Exception as e:
            app.logger.error(f'Login error: {str(e)}')
            flash('An error occurred during login. Please try again.')
            
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # Convert empty string to None for email
        if email == '':
            email = None
        
        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))
        
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            app.logger.info(f'User registered successfully: {username}')
            flash('Registration successful. Please login.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Registration error: {str(e)}')
            flash('An error occurred during registration')
            return redirect(url_for('auth.register'))
            
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

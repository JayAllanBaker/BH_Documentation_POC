from app import app, db
from models import User

with app.app_context():
    # Check if admin user already exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        # Update existing admin
        admin.set_password('password')
        admin.role = 'admin'
    else:
        # Create new admin user
        admin = User(
            username='admin',
            role='admin'
        )
        admin.set_password('password')
        db.session.add(admin)
    
    db.session.commit()
    print("Admin user created/updated successfully")

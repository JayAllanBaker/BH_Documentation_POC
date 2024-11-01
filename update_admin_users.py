from app import app, db
from models import User

def update_admin_users():
    with app.app_context():
        # Create new admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', role='admin')
            admin_user.set_password('passowrd')
            db.session.add(admin_user)
            print("Created new admin user")
        
        # Update tester10's role to admin
        tester10 = User.query.filter_by(username='tester10').first()
        if tester10:
            tester10.role = 'admin'
            print("Updated tester10's role to admin")
        
        db.session.commit()
        print("Changes committed successfully")

if __name__ == '__main__':
    update_admin_users()

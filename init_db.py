from app import app, db
from models import User

def init_database():
    with app.app_context():
        # Drop and recreate all tables
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        
        # Create test user
        print("Creating test user...")
        if not User.query.filter_by(username='test_user').first():
            user = User(username='test_user', role='user')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
            print("Test user created successfully")

if __name__ == '__main__':
    init_database()

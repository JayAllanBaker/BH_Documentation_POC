from app import app, db
from models import User

def create_test_user():
    with app.app_context():
        # Check if test user already exists
        if User.query.filter_by(username='test_provider').first() is None:
            user = User(
                username='test_provider',
                email='test@example.com'
            )
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
            print("Test user created successfully")
        else:
            print("Test user already exists")

if __name__ == "__main__":
    create_test_user()

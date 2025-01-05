from app import app, db  # Import the app and db from your main app file
from app import LicensePlate  # Import the LicensePlate model

def create_database():
    # Create the database and tables
    with app.app_context():
        db.create_all()  # This creates all the tables defined in the models (including LicensePlate)
        print("Database and tables created successfully!")

if __name__ == '__main__':
    create_database()
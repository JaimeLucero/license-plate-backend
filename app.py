from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from flask_cors import CORS

app = Flask(__name__)

# Ensure the 'instance' folder exists
if not os.path.exists('instance'):
    os.makedirs('instance')

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///license_plates.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for frontend (React in this case)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# Initialize the database
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Define the LicensePlate model
class LicensePlate(db.Model):
    __tablename__ = 'license_plate'  # Ensure the correct table name is used
    id = db.Column(db.Integer, primary_key=True)
    license_number = db.Column(db.String(10), nullable=False)  # License number is not primary key anymore
    date = db.Column(db.String(11), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    image_data = db.Column(db.Text, nullable=True)  # Save base64 image as a text field

    # Add a unique constraint for license_number with date and time
    __table_args__ = (db.UniqueConstraint('license_number', 'date', 'time', name='unique_license_date_time'),)

    def __repr__(self):
        return f'<LicensePlate {self.license_number}>'
    
@app.route('/')
def home():
    return 'App is running!'

# Route to get all license plates
@app.route('/license-plates', methods=['GET'])
def get_license_plates():
    plates = LicensePlate.query.all()
    return jsonify([{
        'license_number': plate.license_number,
        'date': plate.date,
        'time': plate.time,
        'image_data': plate.image_data  # Include base64 image data in response
    } for plate in plates])

# Route to add a license plate
@app.route('/license-plates', methods=['POST'])
def add_license_plate():
    data = request.get_json()
    license_number = data.get('license_number')
    date = data.get('date')
    time = data.get('time')
    base64_image = data.get('image')  # The base64 image string

    if not license_number or not date or not time:
        return jsonify({'error': 'Missing data'}), 400

    # Check if the license plate already exists with the same license_number, date, and time
    existing_plate = LicensePlate.query.filter_by(license_number=license_number, date=date, time=time).first()
    if existing_plate:
        return jsonify({'error': 'License plate with this number, date, and time already exists'}), 409

    # Save the new license plate
    new_plate = LicensePlate(license_number=license_number, date=date, time=time, image_data=base64_image)

    try:
        db.session.add(new_plate)
        db.session.commit()
        return jsonify({'message': 'License plate saved successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Database error: {str(e)}"}), 500

# Route to delete a license plate
@app.route('/license-plates/<int:id>', methods=['DELETE'])
def delete_license_plate(id):
    plate = LicensePlate.query.get(id)
    if not plate:
        return jsonify({'error': 'License plate not found'}), 404

    try:
        db.session.delete(plate)
        db.session.commit()
        return jsonify({'message': 'License plate deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Database error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)

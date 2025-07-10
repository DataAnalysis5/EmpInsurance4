import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/employee_management")
client = MongoClient(mongo_uri)
db = client['employee_management']
employees_collection = db['employees']

def ensure_admin_exists():
    if not employees_collection.find_one({'role': 'admin'}):
        employees_collection.insert_one({
            'employee_id': 'admin',
            'name': 'admin',
            'phone': '0000000000',
            'role': 'admin',
            'password': generate_password_hash(os.getenv('ADMIN_PASSWORD', 'admin123')),
            'details_completed': True
        })

ensure_admin_exists()
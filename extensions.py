from flask_wtf import CSRFProtect
from flask_assets import Environment
from pymongo import MongoClient
import os
# Extensions
csrf = CSRFProtect()
assets = Environment()

# MongoDB
# client = MongoClient("mongodb://localhost:27017/employee_management")
# db = client['employee_management']
# employees_collection = db['employees']


mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/employee_management")
client = MongoClient(mongo_uri)
db = client['employee_management']
employees_collection = db['employees']

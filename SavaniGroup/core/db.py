from pymongo import MongoClient
from decouple import config

# Mongo client for making connection with database 
client = MongoClient(config('MONGO_CONNECTION_STRING'))

# Creating database
db = client.Savani_Group
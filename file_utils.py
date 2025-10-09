from pymongo import MongoClient
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "ats_db"
COLLECTION_NAME = "candidates"

def get_db():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db

def load_candidates():
    db = get_db()
    return list(db[COLLECTION_NAME].find({}, {'_id': 0}))

def save_candidate(candidate):
    db = get_db()
    db[COLLECTION_NAME].insert_one(candidate)

def bulk_save_candidates(candidates):
    db = get_db()
    db[COLLECTION_NAME].insert_many(candidates)

def clear_candidates():
    db = get_db()
    db[COLLECTION_NAME].delete_many({})

def update_candidate(name, phone, updates):
    db = get_db()
    db[COLLECTION_NAME].update_one({"name": name, "phone": phone}, {"$set": updates})

def candidate_exists(name, phone):
    db = get_db()
    return db[COLLECTION_NAME].find_one({"name": name, "phone": phone}) is not None

#!/usr/bin/env python3
"""Test MongoDB connectivity from inside the Kubernetes pod or local environment."""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
import sys
import time
from datetime import datetime

def test_connection():
    """Test MongoDB connection with retry logic and database operations."""
    uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    db_name = os.getenv('MONGO_DB_NAME', 'distributive_db')
    
    print(f"Testing connection to: {uri}")
    print(f"Database name: {db_name}")
    print("-" * 50)
    
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            print("✅ MongoDB connection successful!")
            
            # Test database operations
            db = client[db_name]
            
            # Insert test document
            result = db.test_collection.insert_one({
                "test": True,
                "timestamp": datetime.now(),
                "message": "Test document from test_mongo.py"
            })
            print(f"✅ Test document inserted: {result.inserted_id}")
            
            # Find and retrieve document
            found = db.test_collection.find_one({"_id": result.inserted_id})
            if found:
                print(f"✅ Test document retrieved: {found}")
            else:
                print("❌ Test document could not be retrieved")
                return 1
            
            # List collections
            collections = db.list_collection_names()
            print(f"✅ Available collections: {collections}")
            
            # Clean up test document
            db.test_collection.delete_one({"_id": result.inserted_id})
            print("✅ Test document cleaned up")
            
            print("-" * 50)
            print("✅ All tests passed!")
            client.close()
            return 0
            
        except ConnectionFailure as e:
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 2 ** (retry_count - 1)  # Exponential backoff
                print(f"❌ Connection attempt {retry_count}/{max_retries} failed: {e}")
                print(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"❌ MongoDB connection failed after {max_retries} attempts: {e}")
                return 1
        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 1

if __name__ == "__main__":
    sys.exit(test_connection())

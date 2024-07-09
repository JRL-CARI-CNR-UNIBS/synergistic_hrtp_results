import sys
import json
from pymongo import MongoClient
from pymongo.errors import BulkWriteError, ConfigurationError
from bson import ObjectId
from datetime import datetime

def convert_special_fields(document):
    """
    Recursively convert special fields like $oid and $date in a document.
    """
    if isinstance(document, dict):
        for key, value in document.items():
            if isinstance(value, dict):
                # Check for $oid and $date fields and convert them
                if "$oid" in value:
                    document[key] = ObjectId(value["$oid"])
                elif "$date" in value:
                    document[key] = datetime.fromisoformat(value["$date"].replace("Z", "+00:00"))
                else:
                    # Recursively convert inner dictionaries
                    convert_special_fields(value)
            elif isinstance(value, list):
                # Recursively convert lists
                for item in value:
                    convert_special_fields(item)
    elif isinstance(document, list):
        for item in document:
            convert_special_fields(item)
    return document

def import_data_to_mongodb(database_name, collection_name, file_path):
    try:
        # Connect to MongoDB client
        client = MongoClient('mongodb://localhost:27017/')
        
        # Access the database
        db = client[database_name]
        
        # Check if the collection already exists
        if collection_name in db.list_collection_names():
            print(f"Collection '{collection_name}' already exists in database '{database_name}'. Data will not be inserted.")
            return
        
        # Load data from the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Convert special fields in the data
        data = [convert_special_fields(doc) for doc in data]
        
        # Insert data into the collection
        db[collection_name].insert_many(data)
        
        print(f"Data inserted successfully into collection '{collection_name}' of database '{database_name}'.")
        
    except ConfigurationError as ce:
        print(f"MongoDB configuration error: {ce}")
    except BulkWriteError as bwe:
        print(f"Error inserting data: {bwe.details}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Check for arguments passed from the Bash script
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <database_name> <collection_name> <file_path>")
        sys.exit(1)
    
    # Arguments provided by the Bash script
    database_name = sys.argv[1]
    collection_name = sys.argv[2]
    file_path = sys.argv[3]
    
    # Perform the import of data into MongoDB
    import_data_to_mongodb(database_name, collection_name, file_path)

import sys
import json
from pymongo import MongoClient
from pymongo.errors import ConnectionError, BulkWriteError

def import_data_to_mongodb(database_name, collection_name, file_path):
    try:
        # Connect to MongoDB client
        client = MongoClient('mongodb://localhost:27017/')
        
        # Access the database and collection
        db = client[database_name]
        collection = db[collection_name]
        
        # Load data from the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Insert data into the collection
        collection.insert_many(data)
        
        print(f"Data inserted successfully into collection '{collection_name}' of database '{database_name}'.")
        
    except ConnectionError:
        print("Error connecting to MongoDB. Make sure MongoDB is running.")
    except BulkWriteError as bwe:
        print(f"Error inserting data: {bwe.details}")

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

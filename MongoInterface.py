#! /usr/bin/env python3

from dataclasses import dataclass

from pymongo import MongoClient
import pymongo.errors

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
END = '\033[0m'

CONNECTION_LOST = RED + "Connection to Database lost" + END


@dataclass
class MongoInterface:
    database_name: str

    def __post_init__(self):
        client = MongoClient(serverSelectionTimeoutMS=5000)  # 5 seconds of maximum connection wait

        if self.database_name not in client.list_database_names():
            raise Exception

        self.db = client[self.database_name]

    def collection_exist(self, collection_name: str):
        if collection_name not in self.db.list_collection_names():
            return False
        return True

    def query(self, collection_name: str, pipeline: str):
        if not self.collection_exist(collection_name):
            raise Exception(f"Collection {collection_name} is not in database")

        try:
            result = self.db[collection_name].aggregate(pipeline)
        except pymongo.errors.AutoReconnect:
            raise Exception(CONNECTION_LOST)
        return result

    def get_collection(self, collection_name):
        if collection_name not in self.db.list_collection_names():
            raise ValueError("This collection not in db")
        return self.db[collection_name]

from typing import Any, Dict

from pymongo.collection import Collection

def insert(collection: Collection, item: Dict[str, Any]) -> None:
    try:
        collection.insert_one(item)
    except Exception as e:
        print(f"An error occurred while inserting the item: {e}")

def fetchAll(collection: Collection):
    try:
        return list(collection.find({}, {"_id": 0}))
    except Exception as e:
        print(f"An error occurred while fetching all documents: {e}")
        return []

def fetchOne(collection: Collection, query: Dict[str, Any]) -> Any:
    try:
        return collection.find_one(query, {"_id": 0})
    except Exception as e:
        print(f"An error occurred while fetching the document: {e}")
        return None
    
def deleteFirst(collection: Collection):
    l = collection.find().sort('_id', 1).limit(1)
    if l:
        for i in l:
            collection.delete_one({'_id': i['_id']})

def deleteMany(collection: Collection, limit:int):
    l = collection.find().sort('_id', 1).limit(limit)
    if l:
        for i in l:
            collection.delete_one({'_id': i['_id']})
            print(f"Deleted at id {i['_id']}")

from typing import Any, Dict

from pymongo.collection import Collection

def insert(collection: Collection, item: Dict[str, Any]) -> None:
    """
    Inserts a single document into the specified MongoDB collection.

    Args:
        collection (Collection): The MongoDB collection to insert the document into.
        item (Dict[str, Any]): The document to be inserted.

    Returns:
        None: This function does not return anything.

    Raises:
        Exception: If an error occurs while inserting the item.

    Prints:
        str: A message indicating that an error occurred while inserting the item.
    """
    try:
        collection.insert_one(item)
    except Exception as e:
        print(f"An error occurred while inserting the item: {e}")

def fetchAll(collection: Collection):
    """
    Retrieves all documents from a specified MongoDB collection.

    Args:
        collection (Collection): The MongoDB collection to fetch documents from.

    Returns:
        list: A list of documents from the specified collection. If an error occurs, an empty list is returned.

    Raises:
        Exception: If an error occurs while fetching documents.

    Prints:
        str: A message indicating that an error occurred while fetching documents.
    """
    try:
        return list(collection.find({}, {"_id": 0}))
    except Exception as e:
        print(f"An error occurred while fetching all documents: {e}")
        return []

def fetchOne(collection: Collection, query: Dict[str, Any]) -> Any:
    """
    Fetches a single document from a MongoDB collection based on the provided query.

    Args:
        collection (Collection): The MongoDB collection to fetch the document from.
        query (Dict[str, Any]): The query to filter the documents.

    Returns:
        Any: The fetched document, or None if no document is found or an error occurs.

    Raises:
        Exception: If an error occurs while fetching the document.

    Prints:
        str: A message indicating that an error occurred while fetching the document.
    """
    try:
        return collection.find_one(query, {"_id": 0})
    except Exception as e:
        print(f"An error occurred while fetching the document: {e}")
        return None
    
def deleteFirst(collection: Collection):
    """
    Deletes the first document from the specified MongoDB collection.

    Args:
        collection (Collection): The MongoDB collection to delete the document from.

    Returns:
        None

    Raises:
        None

    This function retrieves the first document from the specified collection, sorted by the '_id' field in ascending order, and deletes it. If the collection is empty or an error occurs, no action is taken.

    Note:
        The '_id' field is used to sort and delete the document. If the collection does not have an '_id' field, this function may not work as expected.

    """
    l = collection.find().sort('_id', 1).limit(1)
    if l:
        for i in l:
            collection.delete_one({'_id': i['_id']})

def deleteMany(collection: Collection, limit:int):
    """
    Deletes multiple documents from a MongoDB collection based on the provided limit.

    Args:
        collection (Collection): The MongoDB collection to delete the documents from.
        limit (int): The maximum number of documents to delete.

    Returns:
        None

    This function retrieves the specified number of documents from the collection, sorted by the '_id' field in ascending order, and deletes them. If the collection is empty or an error occurs, no action is taken.

    Note:
        The '_id' field is used to sort and delete the documents. If the collection does not have an '_id' field, this function may not work as expected.

    Example:
        >>> deleteMany(collection, 10)
        Deleted at id ObjectId('...')
        Deleted at id ObjectId('...')
            ...
    """
    l = collection.find().sort('_id', 1).limit(limit)
    if l:
        for i in l:
            collection.delete_one({'_id': i['_id']})
            print(f"Deleted at id {i['_id']}")


def delete(collection: Collection, query: Dict[str, Any]):
    """
    Deletes a single document from a MongoDB collection based on the provided query.

    Args:
        collection (Collection): The MongoDB collection to delete the document from.
        query (Dict[str, Any]): The query to filter the document to be deleted.

    Returns:
        None

    Raises:
        Exception: If an error occurs while deleting the document.

    Prints:
        str: A message indicating that an error occurred while deleting the document.
    """
    try:
        collection.delete_one(query)
    except Exception as e:
        raise(e)
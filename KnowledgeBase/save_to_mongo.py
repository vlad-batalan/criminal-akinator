import json

import pymongo

# Local DB mongo connection.
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")


if __name__ == "__main__":
    json_kb_path = 'Output/json_2024-06-06 12-51-32.json'
    attr_kb_path = 'Output/attr_2024-06-06 12-51-32.json'

    mydb = mongo_client["anime_knowledge_base"]

    # Add metadata if it does not exist.
    # Check if it does not exist.
    metadata_col = mydb['metadata']
    if not metadata_col.find_one():
        # Add new element
        metadata_col.insert_one({ 'target_column': 'Names'})

    # Add knowledge base.
    knowledge_col = mydb['knowledge']
    # Read collection items.
    with open(json_kb_path, 'r') as kb_file:
        items = json.load(kb_file)
        knowledge_col.insert_many(items)

    # Add attributes.
    attr_col = mydb['attributes']
    with open(attr_kb_path, 'r') as attr_file:
        attrs = json.load(attr_file)
        attr_col.insert_many(attrs)

import pymongo

from model.dto.guess_model import Question


class DataRetrievalService:
    __KNOWLEDGE_COLLECTION_NAME = 'knowledge'
    __METADATA_COLLECTION_NAME = 'metadata'
    __ATTRIBUTE_COLLECTION_NAME = 'attributes'

    def __init__(self, connection_str: str, database_name: str):
        self.mongo_client = pymongo.MongoClient(connection_str)
        self.db = self.mongo_client[database_name]

    def get_knowledge_section(self, questions: list[Question]):
        def create_attrib_condition(attr_name, attr_answer):
            return [{attr_name: attr_answer}, {attr_name: {'$exists': False}}]

        knowledge_collection = self.db[DataRetrievalService.__KNOWLEDGE_COLLECTION_NAME]

        # Create query based on questions.
        # There might be items that do not contain the attribute. We do not want to exclude those.
        if questions:
            attribute_condition_list = [{'$or': create_attrib_condition(question.name, question.answer)} for question in
                                        questions]
            query = {'$and': attribute_condition_list}
        else:
            query = {}

        # Projection will remove the attributes that were not provided.
        projection = {question.name: 0 for question in questions}

        print(f"Query the knowledge base: {query}, projecting by {projection}")

        return knowledge_collection.find(query, projection)

    def get_target_field(self) -> str:
        metadata_collection = self.db[DataRetrievalService.__METADATA_COLLECTION_NAME]
        return metadata_collection.find_one().get('target_column')

    def get_attribute_values(self, attribute_name: str) -> list[str]:
        attribute_collection = self.db[DataRetrievalService.__ATTRIBUTE_COLLECTION_NAME]
        query = {'_id': attribute_name}
        projection = {'_id': 0}
        return attribute_collection.find_one(query, projection)['values']

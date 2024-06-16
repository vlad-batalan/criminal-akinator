import time
from collections import Counter

import fastapi
import logging

from model.dto.guess_model import GuessInput, GuessOutput, Question
from service.mongo_service import MongoService
from service.find_question_service import FindQuestionService, FindStrategy

logger = logging.getLogger(__name__)


class GuessService:

    def __init__(self, storage_service: MongoService, find_question_service: FindQuestionService,
                 target_field: str):
        self.storage_service = storage_service
        self.find_question_service = find_question_service
        self.target_field = target_field

    def predict_next_question(self, guess_input: GuessInput,
                              strategy: FindStrategy = FindStrategy.INFORMATION_GAIN) -> GuessOutput:
        start_time = time.time()
        section = self.__get_knowledge_section(guess_input.questions)
        end_time = time.time()
        logger.info(f"[RetrieveTime]: {end_time - start_time} seconds")
        logger.info(f"[RetrieveInstances]: {len(section)}")

        # Treat the case when no character is returned.
        # TODO: Implement strategy to find out the wrong arguments.
        if not len(section):
            raise fastapi.HTTPException(status_code=404, detail="No character was found based on the provided answers!")

        # If maximum depth has been reached, return the majority class.
        if len(guess_input.questions) >= guess_input.max_depth:
            __, majority_class = self.__get_majority(section)
            result = GuessOutput()
            result.guess = majority_class
            return result

        logger.info(f"[Question]: {guess_input.questions}")
        start_time = time.time()
        result = self.find_question_service.find_best_question(section, self.target_field, strategy)
        end_time = time.time()
        logger.info(f"[BestQuestionTime][{strategy}]: {end_time - start_time} seconds.")

        return result

    def __get_knowledge_section(self, attributes: list[Question]) -> list:
        """
            Private method responsible for retrieving a section of the items present in the knowledge base.
            The items are filtered by the answers of the already provided questions and projected after question names that
            were not provided.
        """

        return list(self.storage_service.get_knowledge_section(attributes))

    def __get_majority(self, section: list[dict]) -> (int, str):
        """
           Finds out the majority class and returns it.
        :param section: list of elements provided by __get_knowledge_section() method.
        :return:
            int: the number of classes in the set
            str: the most common label from the target column.
        """

        labels = map(lambda item: item[self.target_field], section)
        counter = Counter(labels)
        most_common = counter.most_common()
        value, __ = most_common[0]
        return len(most_common), value

    def __get_attribute_values(self, attribute) -> list[str]:
        return self.storage_service.get_attribute_values(attribute)

from model.dto.guess_model import GuessOutput, GuessInput
from service.data_retrieval_service import DataRetrievalService
from service.find_question_service import FindQuestionService, FindStrategy
from service.guess_service import GuessService

# Initialize DataRetrievalService.
data_retrieval_service = DataRetrievalService(connection_str='mongodb://localhost:27017/',
                                              database_name="anime_knowledge_base")
target_field = data_retrieval_service.get_target_field()

# Initialize FindQuestionService.
find_question_service = FindQuestionService(target_field)

# Initialize GuessService.
guess_service = GuessService(data_retrieval_service, find_question_service)


def post_guess_prediction(guess_input: GuessInput, strategy: FindStrategy) -> GuessOutput:
    # TODO: Perform parameter validation.

    return guess_service.predict_next_question(guess_input, strategy)

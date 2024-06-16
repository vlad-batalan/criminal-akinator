from model.dto.guess_model import GuessOutput, GuessInput
from service.google_drive_service import GoogleDriveService, MediaCategory
from service.mongo_service import MongoService
from service.find_question_service import FindQuestionService, FindStrategy
from service.guess_service import GuessService

# Initialize FindQuestionService.
find_question_service = FindQuestionService()

# Initialize storage services.
# 1) Anime storage.
anime_storage_service = MongoService(connection_str='mongodb://localhost:27017/',
                                     database_name="anime_knowledge_base")
anime_target_field = anime_storage_service.get_target_field()
anime_guess_service = GuessService(anime_storage_service, find_question_service, anime_target_field)

# 2) Criminal face storage.
creds = "mongodb://localhost:27017/"
with open("resources/MongoCreds.txt", "r") as file:
    creds = file.readline()

criminal_storage_service = MongoService(connection_str=creds,
                                        database_name="CriminalAkinatorDB")
criminal_target_field = criminal_storage_service.get_target_field()
criminal_guess_service = GuessService(criminal_storage_service, find_question_service, criminal_target_field)

# 3) Initialize google drive.
google_drive_service = GoogleDriveService("resources/credentials.json")


def post_guess_prediction_anime(guess_input: GuessInput, strategy: FindStrategy) -> GuessOutput:
    return anime_guess_service.predict_next_question(guess_input, strategy)


def post_guess_prediction_criminals(guess_input: GuessInput, strategy: FindStrategy) -> GuessOutput:
    return criminal_guess_service.predict_next_question(guess_input, strategy)


def retrieve_file_drive(file_name: str, category: MediaCategory):
    return google_drive_service.get_image_url(file_name, category)
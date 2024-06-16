import fastapi

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


def retrieve_question(question: str, set_type: str):
    question_data = None
    if set_type == "anime":
        question_data = anime_storage_service.get_question(question)
    if set_type == "criminal":
        # Return from criminal set.
        question_data = criminal_storage_service.get_question(question)

    if question_data is None:
        raise fastapi.HTTPException(400, "Invalid set type! Use 'anime' or 'criminal'!")

    # Fetch temporary image urls.
    if "metadata" in question_data:
        for element in question_data["metadata"]:
            if "image_id" in element:
                image_id = element["image_id"]
                # Get the image
                element["image_url"] = google_drive_service.get_image_url(image_id, MediaCategory.METADATA)["files"][0][
                    "thumbnailLink"]
    return question_data

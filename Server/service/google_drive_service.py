from enum import Enum

import fastapi
from googleapiclient.discovery import build
from google.oauth2 import service_account


class MediaCategory(Enum):
    CRIMINAL_PROFILE = 0
    ANIME_PROFILE = 1
    METADATA = 2

class GoogleDriveService:

    __CRIMINAL_FOLDER_ID = "1S7W1-h7_14HY1OmZdR6UuMZVZqjlSHOP"
    __ANIME_FOLDER_ID = "1TP8QJoaRIqd3kmWJTV9KSqNRDR8Ii094"
    __METADATA_FOLDER_ID = "183HxLaypaP5RDNwK-F9YaZWhTQFB4TXt"

    def __init__(self, credentials_file_path: str):
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file_path, scopes=['https://www.googleapis.com/auth/drive']
        )

        self.service = build("drive", "v3", credentials=credentials)

    def get_image_url(self, file_name: str, category: MediaCategory):
        folder_id = self.__get_folder_id(category)
        results = self.service.files().list(pageSize=1000,
                                            fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, thumbnailLink)",
                                            q=f'"{folder_id}" in parents and name contains "{file_name}"').execute()
        return results

    def __get_folder_id(self, category: MediaCategory) -> str:
        if category == MediaCategory.CRIMINAL_PROFILE:
            return self.__CRIMINAL_FOLDER_ID
        if category == MediaCategory.ANIME_PROFILE:
            return self.__ANIME_FOLDER_ID
        if category == MediaCategory.METADATA:
            return self.__METADATA_FOLDER_ID

        raise fastapi.HTTPException(status_code=400, detail="Invalid category!")

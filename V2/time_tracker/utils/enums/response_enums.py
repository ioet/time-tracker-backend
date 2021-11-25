from enum import Enum


class ResponseEnums(Enum):
    STATUS_CREATED = 201
    STATUS_OK = 200
    STATUS_BAD_REQUEST = 400
    STATUS_NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

    INVALID_ID = "Invalid Format ID"
    NOT_FOUND = "Not found"
    NOT_CREATED = "could not be created"
    INCORRECT_BODY = "Incorrect body"

    MIME_TYPE = "application/json"

from enum import Enum


class ResponseEnums(Enum):
    INVALID_ID = "Invalid Format ID"
    NOT_FOUND = "Not found"
    NOT_CREATED = "could not be created"
    INCORRECT_BODY = "Incorrect body"

    MIME_TYPE = "application/json"
    INVALID_DATE_FORMAT = "Bad time format, should use date format %m/%d/%Y"

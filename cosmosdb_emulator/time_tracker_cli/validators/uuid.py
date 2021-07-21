import uuid

from prompt_toolkit.validation import Validator, ValidationError


class UUIDValidator(Validator):
    def validate(self, document):
        value_entered = document.text
        try:
            uuid.UUID(value_entered, version=4)
        except ValueError:
            raise ValidationError(
                message='Please provide a valid UUID',
                cursor_position=len(value_entered),
            )

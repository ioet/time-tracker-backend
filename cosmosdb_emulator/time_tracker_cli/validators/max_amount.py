from prompt_toolkit.validation import ValidationError

from cosmosdb_emulator.time_tracker_cli.validators.number import (
    NumberValidator,
)


class MaxAmountValidator(NumberValidator):
    def __init__(self, max_amount, error_message):
        self.max_amount = max_amount
        self.error_message = error_message

    def validate(self, document):
        super().validate(document)

        entered_value = int(document.text)

        if entered_value > self.max_amount:
            raise ValidationError(
                message=self.error_message, cursor_position=len(document.text)
            )

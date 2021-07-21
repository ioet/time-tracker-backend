from prompt_toolkit.validation import Validator, ValidationError


class NumberValidator(Validator):
    def validate(self, document):
        value_entered = document.text
        is_number = value_entered.isnumeric()

        if not is_number:
            raise ValidationError(
                message='Please provide only a numeric value',
                cursor_position=len(value_entered),
            )

        entered_number = int(value_entered)

        if entered_number < 1:
            raise ValidationError(
                message='Please provide numbers greater than 0',
                cursor_position=len(value_entered),
            )

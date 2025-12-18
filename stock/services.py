from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError

from .models import Ingredient, Product, ProductIngredient


def parse_value_br(value: str, msg: str) -> tuple[Decimal | None, list[str]]:
    """Converts a value in Brazilian format (1,234.56) to Decimal in international standard (1234.56).

    Args:
        value(str): Value to be converted.
        msg(str): Message (to return in case of error).

    Returns:
        Decimal, []: If formatting was successful or the number is greater than 9.
        None, errors: If formatting failed or the number is less than or equal to 0.
    """

    errors = []
    try:
        value = value.replace(".", "").replace(",", ".")
        value = Decimal(value)
        if value <= 0:
            errors.append(f"{msg}")
    except (InvalidOperation, AttributeError):
        errors.append(f"{msg}")
        return None, errors
    return value, []

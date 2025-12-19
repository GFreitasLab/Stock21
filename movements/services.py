from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.timezone import is_naive, make_aware
from django.utils.translation import gettext as _

from stock.models import Ingredient, Product

from .models import Movement, MovementInflow, MovementOutflow


def format_period(start: str, end: str) -> tuple[datetime, datetime]:
    """Formats string dates into timezone-aware datetime objects.

    Logic:
        - Converts start and end strings to datetime objects (start at 00:00:00, end at 23:59:59).
        - Validates that the start date is not after the end date.
        - Ensures the date range does not exceed a maximum of 30 days.
        - Converts naive datetime objects to timezone-aware objects.

    Returns:
        tuple: A tuple containing (start_dt, end_dt) as aware datetime objects.

    Raises:
        ValidationError: If dates are invalid, negative, or exceed the 30-day limit.
    """

    try:
        start_dt = datetime.strptime(start + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(end + " 23:59:59", "%Y-%m-%d %H:%M:%S")

        if start_dt > end_dt:
            raise ValidationError(_("The period cannot be negative."))

        if (end_dt - start_dt).days >= 31:
            raise ValidationError(_("The maximum consultation period is 30 days."))

        if is_naive(start_dt):
            start_dt = make_aware(start_dt)
        if is_naive(end_dt):
            end_dt = make_aware(end_dt)
        
        return start_dt, end_dt

    except ValueError as e:
        raise ValidationError(_("Insert a valid date")) from e
    except ValidationError:
        raise


def convert_measures(qte: Decimal, origin: str, destiny: str) -> Decimal:
    """Converts quantities between different measurement units.

    Logic:
        - Uses a mapping of conversion factors (e.g., Grams to Kilograms).
        - Divides by 1000 for g to kg and multiplies by 1000 for kg to g.
        - Returns the original value if origin and destiny units are the same.

    Returns:
        Decimal: The converted quantity.
    """
    factors = {
        ("g", "kg"): lambda x: x / 1000,
        ("kg", "g"): lambda x: x * 1000,
        ("g", "g"): lambda x: x,
        ("kg", "kg"): lambda x: x,
        ("unit", "unit"): lambda x: x,
    }
    return factors[(origin, destiny)](qte)


def parse_value_br(value: str, name: str) -> tuple[Decimal | None, list[str]]:
    """Converts a Brazilian formatted string value to a Decimal.

    Logic:
        - Replaces dots with empty strings and commas with dots to match international standards.
        - Attempts to cast the cleaned string into a Decimal.
        - Validates that the final value is greater than zero.

    Returns:
        tuple: (Decimal, []) if successful, or (None, [error_message]) if failed.
    """

    errors = []
    try:
        value = value.replace(".", "").replace(",", ".")
        value = Decimal(value)
    except (InvalidOperation, AttributeError):
        errors.append(_("Insert a valid value to %(name)s") % {"name": name})
        return None, errors

    if value <= 0:
        errors.append(_("Enter a value greater than 0 to %(name)s") % {"name": name})
        return None, errors
    return value, []


@transaction.atomic
def create_inflow(data: dict, username: str) -> None:
    """Validates and creates an inflow movement for ingredients.

    Logic:
        - Retrieves a list of ingredients from the request data.
        - Parses and validates quantity and price for each ingredient.
        - Converts measurements to match the ingredient's base unit.
        - Updates ingredient stock levels using bulk_update.
        - Records a main Movement and individual MovementInflow logs.

    Returns:
        None: If the transaction is successful.

    Raises:
        ValidationError: If no ingredients are selected or if parsing errors occur.
    """

    errors = []
    ingredients_to_add = []
    value = Decimal("0")

    ingredients_ids = data.getlist("ingredients")
    if not ingredients_ids:
        raise ValidationError([_("Select at least 1 ingredient")])

    for ingredient_id in ingredients_ids:
        ingredient = Ingredient.objects.get(pk=ingredient_id)

        qte_to_add, qte_errors = parse_value_br(data[f"qi-{ingredient_id}"], ingredient.name)

        price, price_errors = parse_value_br(data[f"pi-{ingredient_id}"], ingredient.name)

        if qte_errors or price_errors:
            errors.extend(qte_errors + price_errors)
            continue

        measure = data[f"m-{ingredient_id}"]
        ingredient.qte += convert_measures(qte_to_add, measure, ingredient.measure)

        ingredients_to_add.append((ingredient, qte_to_add, price, measure))
        value += price

    if errors:
        raise ValidationError(errors)

    Ingredient.objects.bulk_update([i[0] for i in ingredients_to_add], ["qte"])

    movement = Movement.objects.create(
        user=username,
        value=value,
        type="in",
        commentary=data["commentary"],
    )

    for ingredient, qte_added, price, measure in ingredients_to_add:
        MovementInflow.objects.create(
            movement=movement,
            name=ingredient.name,
            quantity=qte_added,
            price=price,
            measure=measure,
        )


@transaction.atomic
def create_outflow(data: dict, username: str) -> None:
    """Validates and creates an outflow movement for products.

    Logic:
        - Validates the quantity for each selected product.
        - Checks if there is enough stock for every ingredient in the product's recipe.
        - Deducts necessary ingredient quantities from the stock.
        - Calculates the total transaction value based on product prices.
        - Records a main Movement and individual MovementOutflow logs.

    Returns:
        None: If the transaction is successful.

    Raises:
        ValidationError: If no products are selected, if parsing fails, or if stock is insufficient.
    """

    errors = []
    products_sold = []
    total_value = Decimal("0")

    products_ids = data.getlist("products")
    if not products_ids:
        raise ValidationError([_("Select at least 1 product")])

    for product_id in products_ids:
        product = Product.objects.get(pk=product_id)
        ingredients_to_reduce = []
        product_errors = []

        quantity, qte_error = parse_value_br(data[f"qp-{product_id}"], product.name)

        if qte_error:
            product_errors.extend(qte_error)
            continue

        if quantity:
            for recipe_item in product.productingredient_set.all():
                ingredient = recipe_item.ingredient
                decrease_qte = recipe_item.quantity * quantity
                remaining = ingredient.qte - decrease_qte

                if remaining < 0:
                    product_errors.append(_("Insufficient stock for ingredient %(ingredient)s!") % {"ingredient": ingredient.name})
                else:
                    ingredient.qte = remaining
                    ingredients_to_reduce.append(ingredient)

        if product_errors:
            errors.extend(product_errors)
            continue

        value = product.price * quantity
        total_value += value

        Ingredient.objects.bulk_update(ingredients_to_reduce, ["qte"])
        products_sold.append((product.name, quantity, value))

    if errors:
        raise ValidationError(errors)

    movement = Movement.objects.create(
        user=username,
        value=total_value,
        type="out",
        commentary=data["commentary"],
    )

    for name, quantity, price in products_sold:
        MovementOutflow.objects.create(
            movement=movement,
            name=name,
            quantity=quantity,
            price=price,
        )

from django.core.exceptions import ValidationError

from .models import CustomUser


def validate_email(email: str, account_id=None) -> list:
    """Validates if an email is unique in the database.

    Args:
        email: The email string to be checked.
        account_id: The ID of the current account (optional). Used to exclude 
            the current user from the uniqueness check during updates.

    Returns:
        A list of error messages. If the list is empty, the email is valid.
    """

    errors = []
    if account_id:
        exists = CustomUser.objects.filter(email=email).exclude(id=account_id).exists()
    else:
        exists = CustomUser.objects.filter(email=email).exists()
    if exists:
        errors.append("Já existe uma conta com esse email.")
    return errors


def validate_password(password: str, confirm_password: str) -> list:
    """Validates the password strength and confirmation match.

    Args:
        password: The primary password string.
        confirm_password: The password confirmation string to match against.

    Returns:
        A list of error messages regarding password mismatch or length.
    """

    errors = []
    if password != confirm_password:
        errors.append("As senhas devem ser iguais!")
    if len(password) < 8:
        errors.append("A senha deve ter no mínimo 8 caracteres!")
    return errors


def create_account(data: dict) -> CustomUser:
    """Handles the creation of a new user account after validation.

    Args:
        data: A dictionary containing user details (email, password, 
            confirm_password, first_name, last_name, and role).

    Returns:
        The newly created CustomUser instance.

    Raises:
        ValidationError: If any email or password validation fails.
    """

    errors = []

    errors.extend(validate_email(data["email"]))
    errors.extend(validate_password(data["password"], data["confirm_password"]))

    if errors:
        raise ValidationError(errors)

    account = CustomUser.objects.create_user(
        username=data["email"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        role=data["role"],
        password=data["password"],
    )

    return account


def update_account(account: CustomUser, data: dict):
    """Updates the information of an existing user account.

    Args:
        account: The CustomUser instance to be updated.
        data: A dictionary containing the updated fields (first_name, 
            last_name, email, role, and optionally password fields).

    Returns:
        The updated CustomUser instance.

    Raises:
        ValidationError: If the new password data is provided but invalid.
    """

    error = []

    password, confirm_password = data["password"], data["confirm_password"]
    if password and confirm_password:
        error = validate_password(password, confirm_password)

    if error:
        raise ValidationError(error)

    account.first_name = data["first_name"]
    account.last_name = data["last_name"]
    account.email = data["email"]
    account.role = data["role"]

    return account

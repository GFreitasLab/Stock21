from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# Customizing User Model
class CustomUser(AbstractUser):
    """Represents a User.

    Atributes:
        first_name (str): Name.
        last_name (str): Last Name.
        email (str): Email.
        role (str): Role (employee/admin).
        created_at (timestamp): Creation Date.
        updated_at (timestamp): Update Date.

    """

    email = models.EmailField(max_length=100, unique=True)
    role = models.CharField(
        max_length=20,
        choices=[("employee", _("Employee")), ("admin", _("Administrator"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # Auth via Email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "role"]

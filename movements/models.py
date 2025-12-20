from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.formats import number_format


class Movement(models.Model):
    """Represents a Movement.

    Atributes:
        user (str): Name of the person responsible for the movement.
        value (Decimal): Total movement Value.
        type (str): Type of Movement (in/out).
        date (timestamp): Date of Movement.
        commentary (str): Commentary about Movement.

    """

    user = models.CharField(max_length=100)
    value = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=([("in", _("Inflow")), ("out", _("Outflow"))]))
    date = models.DateTimeField(auto_now_add=True)
    commentary = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.date} - {self.user}: {self.value}"


class MovementInflow(models.Model):
    """Represents an incoming Movement (ingredients).

    Atributes:
        movement (Fk): Foreign key for the base movement with the name ingredients.
        name (str): Ingredient name.
        quantity (Decimal): Amount added.
        price (Decimal): Price paid.
        measure (str) Measure unit (g/kg/unit).

    """

    # related_name to perform reverse access and retrieve this information
    movement = models.ForeignKey(Movement, on_delete=models.CASCADE, related_name="ingredients")
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    measure = models.CharField(max_length=10, choices=([("g", _("Grams")), ("kg", _("Kilograms")), ("unit", _("Units"))]))

    @property
    def quantity_display(self):
        """Returns the quantity based on measure"""
        if self.measure == "kg":
            return number_format(self.quantity, 3)
        return number_format(self.quantity, 0)

    def __str__(self):
        return f"{self.name}: {self.quantity} - {self.price}"


class MovementOutflow(models.Model):
    """Represents an outgoing movement (products).

    Atributes:
        movement (Fk): Foreign key for the base movement with the name products.
        name (str): Product name.
        quantity (int): Quantity sold.
        price (Decimal): Price.

    """

    # Reverse access here too
    movement = models.ForeignKey(Movement, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name}: {self.quantity} - {self.price}"

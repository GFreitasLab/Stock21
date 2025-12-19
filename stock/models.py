from django.db import models
from django.utils.translation import gettext as _


class Category(models.Model):
    """Represents a category of ingredients.

    Attributes:
        name (str): Category name.
        description (str): Optional description.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Represents an ingredient used in products.

    Attributes:
        name (str): Name of the ingredient.
        category (Category): Category to which the ingredient belongs.
        qty (Decimal): Current quantity available in stock.
        min_qty (int): Minimum safety quantity in stock.
        measure (str): Unit of measurement for the ingredient (g/kg/unit).
    """

    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    qte = models.DecimalField(default=0, max_digits=10, decimal_places=3)
    min_qte = models.DecimalField(default=0, max_digits=10, decimal_places=3)
    measure = models.CharField(max_length=10, choices=([("g", _("Grams")), ("kg", _("Kilograms")), ("unit", _("Units"))]))

    def __str__(self):
        return self.name


class Product(models.Model):
    """Represents a product available for sale.

    Attributes:
        name (str): Product name.
        ingredients (QuerySet[Ingredient]): Required ingredients, related through the ProductIngredient table.
        price (Decimal): Product price.
        unit (int): Product quantity (in the case of beverages)
    """

    name = models.CharField(max_length=100, unique=True)
    ingredients = models.ManyToManyField(
        Ingredient, through="ProductIngredient", through_fields=("product", "ingredient"), blank=True
    )
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


# Intermediate table for managing the ingredients and quantities of each product
class ProductIngredient(models.Model):
    """Represents the relationship between products and ingredients.

    Defines the quantity of each ingredient used
    in the composition of a product.

    Attributes:
        product (Product): Associated product.
        ingredient (Ingredient): Associated ingredient.
        quantity (Decimal): Quantity of ingredient required for the product.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = ("product", "ingredient")

    def __str__(self):
        return f"{self.product} - {self.ingredient}: {self.quantity}"

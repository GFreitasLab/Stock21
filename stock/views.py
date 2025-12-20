from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _
from django.utils.formats import sanitize_separators
from decimal import Decimal

from core.decorators import admin_required

from .models import Category, Ingredient, Product, ProductIngredient


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def category_create(request: HttpRequest) -> HttpResponse:
    """Creates a new category.

    GET:
        Renders the category creation form.

    POST:
        - Creates a new category if the name does not exist.
        - If it already exists, redirects to the list displaying an error message.

    Returns:
        HttpResponse: Creation page (invalid GET or POST).
        HttpResponseRedirect: Redirects to the category list after creation or error.
    """

    if request.method == "GET":
        return render(request, "category_create.html")

    name = request.POST.get("name")
    description = request.POST.get("description")

    if Category.objects.filter(name__iexact=name):
        messages.error(request, _("The category you want to register already exists!"))
        return redirect("category_list")

    category = Category.objects.create(name=name, description=description)

    category.save()

    messages.success(request, _("Category successfully created!"))
    return redirect("category_list")


@login_required
@admin_required
@require_http_methods(["GET"])
def category_list(request: HttpRequest) -> HttpResponse:
    """Lists all registered categories, with pagination.

    GET:
        Renders the paginated list of categories.

    Returns:
        HttpResponse: Page with the list of categories.
    """

    categories = Category.objects.all()

    page_number = request.GET.get("page") or 1
    paginator = Paginator(categories, 10)

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "Paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
    }
    return render(request, "category_list.html", context)


@login_required
@admin_required
@require_http_methods(["GET"])
def category_detail(request: HttpRequest, id: int) -> HttpResponse:
    """Displays the details of a specific category.

    Args:
        id (int): Unique identifier of the category.

    GET:
        Renders the category details page.

    Returns:
        HttpResponse: Page with category details.
    """

    context = {"category": get_object_or_404(Category, id=id)}
    return render(request, "category_detail.html", context)


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def category_update(request: HttpRequest, id: int) -> HttpResponse:
    """Updates an existing category.

    Args:
        id (int): Unique identifier for the category.

    GET:
        Renders the form with the current category data.

    POST:
        - Updates name and description.
        - If the name already exists in another category, displays an error message.

    Returns:
        HttpResponse: Edit page (invalid GET or POST).
        HttpResponseRedirect: Redirects to the category list after updating.
    """

    category = get_object_or_404(Category, id=id)
    context = {"category": category}

    if request.method == "GET":
        return render(request, "category_update.html", context)

    name = request.POST.get("name")

    if Category.objects.filter(name__iexact=name).exclude(id=category.id).exists():
        messages.error(request, _("The new name you want to enter is already associated with a category!"))
        return render(request, "category_update.html", context)

    category.name = name
    category.description = request.POST.get("description")
    category.save()

    messages.success(request, _("Category successfully changed!"))
    return redirect("category_list")


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def category_delete(request: HttpRequest, id: int) -> HttpResponse:
    """Deletes an existing category.

    Args:
        id (int): Unique identifier for the category.

    GET:
        Renders the deletion confirmation page.

    POST:
        - Validates the authenticated user's password.
        - Removes the category if the password is correct.

    Returns:
        HttpResponse: Deletion confirmation page (GET).
        HttpResponseRedirect: Redirects to the list after deletion or password error.
    """

    category = get_object_or_404(Category, id=id)

    if request.method == "GET":
        context = {"category": category}
        return render(request, "category_delete.html", context)

    password = request.POST.get("password")

    if not request.user.check_password(password):
        messages.error(request, _("The password you entered is incorrect!"))
        return redirect("category_list")

    category.delete()

    messages.success(request, _("Category successfully deleted!"))
    return redirect("category_list")


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def ingredient_create(request: HttpRequest) -> HttpResponse:
    """Creates a new ingredient.

    GET:
        Renders the ingredient creation form.

    POST:
        - Creates an ingredient associated with a category.
        - Validates unique name, quantities, and measurement.
        - If any data is invalid, returns the form filled with errors.

    Returns:
        HttpResponse: Creation page (invalid GET or POST).
        HttpResponseRedirect: Redirects to the list of ingredients after creation.
    """

    context = {
        "categories": Category.objects.all(),
        "measure_choices": Ingredient._meta.get_field("measure").choices,
    }

    if request.method == "GET":
        return render(request, "ingredient_create.html", context)

    try:
        name = request.POST.get("name")
        category_id = request.POST.get("category")
        measure = request.POST.get("measure")

        category = get_object_or_404(Category, id=category_id)

        if Ingredient.objects.filter(name__iexact=name).exists():
            raise ValidationError(_("The ingredient you want to register already exists!"))

        errors = []

        qte = request.POST.get("qte")
        try:
            qte = Decimal(sanitize_separators(qte))
            if qte < 1:
                errors.append(_("Enter a quantity greater than 0"))
        except:
            errors.append(_("Please enter a valid quantity!"))

        min_qte = request.POST.get("min_qte")
        try:
            min_qte = Decimal(sanitize_separators(min_qte))
            if min_qte < 1:
                errors.append(_("Enter a quantity greater than 0"))
        except:
            errors.append(_("Please enter a valid minimum quantity!"))

        if errors:
            raise ValidationError(errors)

        ingredient = Ingredient.objects.create(
            name=name,
            category=category,
            qte=qte,
            min_qte=min_qte,
            measure=measure,
        )

        ingredient.save()

        messages.success(request, _("Ingredient successfully registered!"))
        return redirect("ingredient_list")

    except ValidationError as e:
        for msg in e.messages:
            messages.error(request, msg)
        context["old_data"] = request.POST
        return render(request, "ingredient_create.html", context)


@login_required
@require_http_methods(["GET"])
def ingredient_list(request: HttpRequest) -> HttpResponse:
    """Lists all registered ingredients, with filters and pagination.

    GET:
        - Allows filtering by name, category, quantity, or minimum quantity.
        - Renders the paginated list of ingredients.

    Returns:
        HttpResponse: Page with the list of ingredients.
    """

    ingredients = Ingredient.objects.all()
    categories = Category.objects.all()

    field = request.GET.get("field")
    value = request.GET.get("value")

    if field and value:
        match field:
            case "name":
                ingredients = ingredients.filter(name__icontains=value)
            case "category":
                ingredients = ingredients.filter(category__name__icontains=value)
            case "qte":
                ingredients = ingredients.filter(qte=value)
            case "min_qte":
                ingredients = ingredients.filter(min_qte=value)

    page_number = request.GET.get("page") or 1
    paginator = Paginator(ingredients, 10)

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "Paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "categories": categories,
        "field": field,
        "value": value,
    }
    return render(request, "ingredient_list.html", context)


@login_required
@require_http_methods(["GET"])
def ingredient_detail(request: HttpRequest, id: int) -> HttpResponse:
    """Displays the details of a specific ingredient.

    Args:
        id (int): Unique identifier of the ingredient.

    GET:
        Renders the ingredient details page.

    Returns:
        HttpResponse: Page with the ingredient details.
    """

    context = {"ingredient": get_object_or_404(Ingredient, id=id)}
    return render(request, "ingredient_detail.html", context)


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def ingredient_update(request: HttpRequest, id: int) -> HttpResponse:
    """Updates an existing ingredient.

    Args:
        id (int): Unique identifier of the ingredient.

    GET:
        Renders the form with the current ingredient data.

    POST:
        - Updates name, category, quantities, and measurement.
        - Validates unique name and numeric values.
        - If any data is invalid, displays an error message.

    Returns:
        HttpResponse: Edit page (invalid GET or POST).
        HttpResponseRedirect: Redirects to the list of ingredients after updating.
    """

    ingredient = get_object_or_404(Ingredient, id=id)
    context = {
        "ingredient": ingredient,
        "categories": Category.objects.all(),
        "measure_choices": Ingredient._meta.get_field("measure").choices,
    }
    if request.method == "GET":
        return render(request, "ingredient_update.html", context)

    try:
        name = request.POST.get("name")

        if Ingredient.objects.filter(name__iexact=name).exclude(id=ingredient.id).exists():
            raise ValidationError(_("The new name you want to enter is already associated with an ingredient."))

        errors = []

        qte = request.POST.get("qte")
        try:
            qte = Decimal(sanitize_separators(qte))
            if qte < 1:
                errors.append(_("Enter a quantity greater than 0"))
        except:
            errors.append(_("Please enter a valid quantity!"))

        min_qte = request.POST.get("min_qte")
        try:
            min_qte = Decimal(sanitize_separators(min_qte))
            if min_qte < 1:
                errors.append(_("Enter a minimum quantity greater than 0"))
        except:
            errors.append(_("Please enter a valid minimum quantity!"))

        if errors:
            raise ValidationError(errors)

        ingredient.name = name
        category_id = request.POST.get("category")
        ingredient.category = get_object_or_404(Category, id=category_id)
        ingredient.qte = qte
        ingredient.min_qte = min_qte
        ingredient.measure = request.POST.get("measure")

        ingredient.save()

        messages.success(request, _("Ingredient successfully changed!"))
        return redirect("ingredient_list")

    except ValidationError as e:
        for msg in e.messages:
            messages.error(request, msg)
        return render(request, "ingredient_update.html", context)


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def ingredient_delete(request: HttpRequest, id: int) -> HttpResponse:
    """Deletes an existing ingredient.

    Args:
        id (int): Unique identifier of the ingredient.

    GET:
        Renders the deletion confirmation page.

    POST:
        - Validates the authenticated user's password.
        - Removes the ingredient if the password is correct.

    Returns:
        HttpResponse: Confirmation page (GET).
        HttpResponseRedirect: Redirects to the list after deletion or password error.
    """

    ingredient = get_object_or_404(Ingredient, id=id)

    if request.method == "GET":
        context = {"ingredient": ingredient}
        return render(request, "ingredient_delete.html", context)

    password = request.POST.get("password")

    if not request.user.check_password(password):
        messages.error(request,_("The password you entered is incorrect!"))
        return redirect("ingredient_list")

    ingredient.delete()

    messages.success(request, _("Ingredient successfully deleted!"))
    return redirect("ingredient_list")


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def product_create(request: HttpRequest) -> HttpResponse:
    """Creates a new product with associated ingredients.

    GET:
        Renders the product creation form.

    POST:
        - Creates the product with name, price, and ingredients.
        - Validates unique name, price, and quantities.
        - If any data is invalid, returns the form filled with errors.

    Returns:
        HttpResponse: Creation page (invalid GET or POST).
        HttpResponseRedirect: Redirects to the product list after creation.
    """

    context = {"ingredients": Ingredient.objects.all()}

    if request.method == "GET":
        return render(request, "product_create.html", context)

    try:
        name = request.POST.get("name")

        if Product.objects.filter(name__iexact=name).exists():
            raise ValidationError(_("The product you want to create already exists!"))

        raw_price = request.POST.get("price")

        errors = []

        try:
            price = Decimal(sanitize_separators(raw_price))
            if price < 1:
                errors.append(_("Enter a price greater than 0"))
        except:
            errors.append(_("Enter a valid price!"))

        ingredients_ids = request.POST.getlist("ingredients")
        if not ingredients_ids:
            raise ValidationError([_("Select at least 1 ingredient!")])
        ingredients_to_create = []
        for ingredient_id in ingredients_ids:
            quantity = request.POST.get(f"q-{ingredient_id}")

            try:
                quantity = Decimal(sanitize_separators(quantity))
                if quantity < 1:
                    errors.append(_("Enter a quantity greater than 0"))
            except:
                errors.append(_("Insert a valid quantity to %(ingredient)s!") % {"ingredient": Ingredient.objects.get(pk=ingredient_id).name})
                continue

            ingredients_to_create.append((int(ingredient_id), quantity))

        if errors:
            raise ValidationError(errors)

        product = Product.objects.create(name=name, price=price)

        for ingredient_id, quantity in ingredients_to_create:
            ProductIngredient.objects.create(
                product=product,
                ingredient_id=ingredient_id,
                quantity=quantity,
            )

        messages.success(request, _("Product sucessfully created!"))
        return redirect("product_list")

    except ValidationError as e:
        for msg in e.messages:
            messages.error(request, msg)
        context["old_data"] = request.POST
        quantities = {key[2:]: value for key, value in request.POST.items() if key.startswith("q-")}

        ingredients_with_data = []
        for ingredient in Ingredient.objects.all():
            ingredient.quantity = quantities.get(str(ingredient.id), "")
            ingredients_with_data.append(ingredient)

        context["ingredients"] = ingredients_with_data
        return render(request, "product_create.html", context)


@login_required
@admin_required
@require_http_methods(["GET"])
def product_list(request: HttpRequest) -> HttpResponse:
    """Lists all registered products, with filters and pagination.

    GET:
        - Allows filtering by name or price.
        - Renders the paginated list of products.

    Returns:
        HttpResponse: Page with the list of products.
    """

    products = Product.objects.all()

    field = request.GET.get("field")
    value = request.GET.get("value")

    if field and value:
        match field:
            case "name":
                products = products.filter(name__icontains=value)
            case "price":
                try:
                    value = Decimal(sanitize_separators(value))
                except:
                    messages.error(request, _("Please enter a valid price!"))
                    return redirect("product_list")

                products = products.filter(price=value)

    page_number = request.GET.get("page") or 1
    paginator = Paginator(products, 10)

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "Paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "field": field,
        "value": value,
    }
    return render(request, "product_list.html", context)


@login_required
@admin_required
@require_http_methods(["GET"])
def product_detail(request: HttpRequest, id: int) -> HttpResponse:
    """Displays the details of a specific product, including its ingredients.

    Args:
        id (int): Unique product identifier.

    GET:
        Renders the product details page.

    Returns:
        HttpResponse: Page with product details.
    """

    product = get_object_or_404(Product, id=id)
    context = {
        "product": product,
        "products_ingredients": product.productingredient_set.all(),
    }
    return render(request, "product_detail.html", context)


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def product_update(request: HttpRequest, id: int) -> HttpResponse:
    """Updates an existing product and its ingredients.

    Args:
        id (int): Unique product identifier.

    GET:
        Renders the form with the current product data.

    POST:
        - Updates name, price, and associated ingredients.
        - Validates unique name, price, and quantities.
        - Adds or removes ingredients as selected.

    Returns:
        HttpResponse: Edit page (GET or POST invalid).
        HttpResponseRedirect: Redirects to the product list after updating.
    """

    product = get_object_or_404(Product, id=id)

    context = {
        "product": product,
        "ingredients": Ingredient.objects.all(),
        "product_ingredients": product.productingredient_set.all(),
    }

    if request.method == "GET":
        return render(request, "product_update.html", context)

    try:
        name = request.POST.get("name")

        if Product.objects.filter(name__iexact=name).exclude(id=product.id).exists():
            raise ValidationError(_("The new name you want to enter is already associated with a product!"))

        raw_price = request.POST.get("price")

        try:
            price = Decimal(sanitize_separators(raw_price))
            if price < 1:
                raise ValidationError([_("Enter a price greater than 0")])
        except:
            raise ValidationError([_("Please enter a valid price!")])

        selected_ids = request.POST.getlist("ingredients")
        if not selected_ids:
            raise ValidationError([_("Please enter at least 1 ingredient!")])

        product.name = name
        product.price = price
        product.save(update_fields=["name", "price"])

        old_ingredients_ids = set(product.productingredient_set.values_list("ingredient_id", flat=True))
        new_ingredients_ids = set(int(pk) for pk in selected_ids)

        ids_to_remove = old_ingredients_ids - new_ingredients_ids

        if ids_to_remove:
            ProductIngredient.objects.filter(product=product, ingredient_id__in=ids_to_remove).delete()

        errors = []
        ingredients_list = []
        for ingredient_id in new_ingredients_ids:
            quantity = request.POST.get(f"q-{ingredient_id}")

            try:
                quantity = Decimal(sanitize_separators(quantity))
                if quantity < 1:
                    errors.append(_("Enter a quantity greater then 0 for the ingredient %(ingredient)s!") % {"ingredient": Ingredient.objects.get(pk=ingredient_id).name})
            except:
                errors.append(_("Enter a valid quantity for the ingredient %(ingredient)s!") % {"ingredient": Ingredient.objects.get(pk=ingredient_id).name})
                continue

            ingredients_list.append((ingredient_id, quantity))

        if errors:
            raise ValidationError(errors)

        for ingredient_id, quantity in ingredients_list:
            ProductIngredient.objects.update_or_create(
                product=product,
                ingredient_id=ingredient_id,
                defaults={"quantity": quantity},
            )

        messages.success(request, _("Product successfully changed!"))
        return redirect("product_list")

    except ValidationError as e:
        for msg in e:
            messages.error(request, msg)
        return render(request, "product_update.html", context)


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def product_delete(request: HttpRequest, id: int) -> HttpResponse:
    """Deletes an existing product.

    Args:
        id (int): Unique product identifier.

    GET:
        Renders the deletion confirmation page.

    POST:
        - Validates the authenticated user's password.
        - Removes the product if the password is correct.

    Returns:
        HttpResponse: Confirmation page (GET).
        HttpResponseRedirect: Redirects to the list after deletion or password error.
    """

    product = get_object_or_404(Product, id=id)

    if request.method == "GET":
        context = {"product": product}
        return render(request, "product_delete.html", context)

    password = request.POST.get("password")

    if not request.user.check_password(password):
        messages.error(request, _("The password you entered is incorrect!"))
        return redirect("product_list")

    product.delete()

    messages.success(request, _("Product successfully deleted!"))
    return redirect("product_list")

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth import logout as logout_django
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _

from core.decorators import admin_required

from .models import CustomUser
from .services import create_account, update_account


@require_http_methods(["GET", "POST"])
def login(request: HttpRequest) -> HttpResponse:
    """Renders the login page and processes user authentication.

    Args:
        request (HttpRequest): Django request object.

    GET:
        Renders the login screen with a blank form.

    POST:
        Validates the email and password provided:
            - If valid, redirects to the home page.
            - If invalid, redirects back to the login page with an error message.

    Returns:
        HttpResponse: Login page (GET or POST with invalid data).
        HttpResponseRedirect: Redirect to home page (valid POST).
    """

    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, "login.html")

    email = request.POST.get("email")
    password = request.POST.get("password")

    if not email or not password:
        messages.error(request,_( "Fill in all fields"))
        return render(request, "login.html", {"email": email})

    user = authenticate(email=email, password=password)

    if user:
        login_django(request, user)
        return redirect("home")
    messages.error(request, _("Email or Password inválid!"))
    return render(request, "login.html", {"email": email})


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def register(request: HttpRequest) -> HttpResponse:
    """Renders the registration page and processes the user registration.

    Args:
        request (HttpRequest): Django request object.

    GET:
        Renders the registration screen with a blank form.

    POST:
        Validates the fields provided:
            - If valid, adds the new user to the database and redirects to the user list with a message confirming the action.
            - If invalid, redirects again with an error message to the registration page filled with the data.

    Returns:
        HttpResponse: Registration page (GET or POST with invalid data).
        HttpResponseRedirect: Redirect to the user list page (valid POST).
    """

    context = {"role_choices": CustomUser._meta.get_field("role").choices}

    if request.method == "GET":
        return render(request, "register.html", context)

    try:
        user = create_account(request.POST)

        user.save()

        messages.success(request, _("User sucessfully created!"))
        return redirect("account_list")

    except ValidationError as e:
        for msg in e.messages:
            messages.error(request, msg)
        context["old_data"] = request.POST
        return render(request, "register.html", context)


@login_required
@require_http_methods(["POST"])
def logout(request: HttpRequest) -> HttpResponse:
    """Performs the user logout process.

    Args:
        request (HttpRequest): Django request object.

    POST:
        Sends a request asking for logout.

    Returns:
        HttpResponseRedirect: Redirects to the login page.
    """

    logout_django(request)
    messages.success(request, _("sucessfully Logged out!"))
    return redirect("login")


@login_required
@admin_required
@require_http_methods(["GET"])
def account_list(request: HttpRequest) -> HttpResponse:
    """Renders a list containing the system users.

    Args:
        request (HttpRequest): Django request object.

    GET:
        Renders the users screen with an empty filter:
            - If there is a filter, returns the elements that match the filter.
            - If there is no filter, returns the elements according to the page.

    Returns:
        HttpResponse: Page listing the users.
    """

    accounts = CustomUser.objects.all()

    field = request.GET.get("field")
    value = request.GET.get("value")

    if field and value:
        match field:
            case "first_name":
                accounts = accounts.filter(first_name__icontains=value)
            case "email":
                accounts = accounts.filter(email=value)
            case "role":
                accounts = accounts.filter(role=value)

    page_number = request.GET.get("page") or 1
    paginator = Paginator(accounts, 10)

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "Paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "role_choices": CustomUser._meta.get_field("role").choices,
        "field": field,
        "value": value,
    }
    return render(request, "account_list.html", context)


@login_required
@admin_required
@require_http_methods(["GET"])
def account_detail(request: HttpRequest, id: int) -> HttpResponse:
    """Renders a page with user details.

    Args:
        request (HttpRequest): Django request object.
        id (int): unique user identifier.

    GET:
        Renders the screen with user data.

    Returns:
        HttpResponse: Detail page.
    """

    account = get_object_or_404(CustomUser, id=id)

    return render(request, "account_detail.html", {"account": account})


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def account_update(request: HttpRequest, id: int) -> HttpResponse:
    """Renders the update page with the user's data.

    Args:
        request (HttpRequest): Django request object.
        id (int): unique user identifier.

    GET:
        Renders the registration screen with the form filled in with the user's data.

    POST:
        Validates the fields provided:
            - If valid, changes the user in the database and redirects to the user list with a message confirming the action.
            - If invalid, redirects back to the change page filled with the data with an error message.

    Returns:
        HttpResponse: Registration page (GET or POST with invalid data).
        HttpResponseRedirect: Redirect to the user list page (valid POST).
    """

    account = get_object_or_404(CustomUser, id=id)
    context = {"account": account, "role_choices": CustomUser._meta.get_field("role").choices}

    if request.method == "GET":
        return render(request, "account_update.html", context)

    try:
        account = update_account(account, request.POST)

        account.save()

        messages.success(request, _("Account sucessfully changed!"))
        return redirect("account_list")
    except ValidationError as e:
        for msg in e.messages:
            messages.error(request, msg)
        return render(request, "account_update.html", context)


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def account_delete(request, id):
    """Displays and processes user deletion.

    Args:
        request (HttpRequest): Django request object.
        id (int): unique user identifier.

    GET:
        Renders the user deletion screen requesting a password.

    POST:
        Validates the password:
            - If valid, deletes the user from the database with a success message.
            - If invalid, redirects to the password entry page with an error message.

    Returns:
        HttpResponse: User deletion page (invalid password).
        HttpResponseRedirect: Redirect to the user list page (valid POST).
    """

    account = get_object_or_404(CustomUser, id=id)
    context = {"account": account}

    if request.method == "GET":
        return render(request, "account_delete.html", context)

    else:
        password = request.POST.get("password")

        if not request.user.check_password(password):
            messages.error(request, _("The password you entered is incorrect!"))
            return render(request, "account_delete.html", context)

        account.delete()

        messages.success(request, _("Account successfully deleted!"))
        return redirect("account_list")

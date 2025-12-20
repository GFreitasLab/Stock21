from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _
from django.utils.formats import number_format
from fpdf import FPDF

from core.decorators import admin_required
from stock.models import Ingredient, Product

from .models import Movement
from .services import create_inflow, create_outflow, format_period


@login_required
@require_http_methods(["GET", "POST"])
def movement_create(request: HttpRequest) -> HttpResponse:
    """Renders the transaction creation page and processes the record.

    Args:
        request (HttpRequest): Django request object.

    GET:
        Renders the transaction record screen with ingredients and products to be transacted.

    POST:
        Validates the fields provided according to the transaction type:
            - If valid, redirects to the transaction list and displays a success message.
            - If invalid, redirects to the creation page again and displays an error message.

    Returns:
        HttpResponse: Movement creation page (GET or POST with invalid data).
        HttpResponseRedirect: Redirect to the list of movements (valid POST).
    """

    context = {
        "products": Product.objects.all(),
        "ingredients": Ingredient.objects.all(),
        "type_choices": Movement._meta.get_field("type").choices,
    }

    if request.method == "GET":
        return render(request, "movement_create.html", context)

    try:
        user = request.user
        username = f"{user.first_name} {user.last_name}"
        transaction_type = request.POST.get("type")

        match transaction_type:
            case "in":
                create_inflow(request.POST, username)
            case "out":
                create_outflow(request.POST, username)

        messages.success(request, _("Movement successfully recorded!"))
        return redirect("movement_list")

    except ValidationError as e:
        for msg in e.messages:
            messages.error(request, msg)
        return render(request, "movement_create.html", context)


@login_required
@require_http_methods(["GET"])
def movement_list(request: HttpRequest) -> HttpResponse:
    """Displays a list of system transactions.

    Args:
        request (HttpRequest): Django request object.

    GET:
        Renders the transaction screen with an empty date filter.
        - If there is a filter, returns the transactions corresponding to the period.
        - If there is no filter, returns the transactions according to the page.

    Returns:
        HttpResponse: Listing the transactions.
    """

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    start_dt, end_dt = None, None
    has_error = False

    if start_date and end_date:
        try:
            start_dt, end_dt = format_period(str(start_date), str(end_date))
        except ValidationError as e:
            messages.error(request, e.message)
            has_error = True

        movements = Movement.objects.filter(date__range=(start_dt, end_dt)).order_by("-date")

    if not start_dt or not end_dt or has_error:
        movements = Movement.objects.all().order_by("-date")

    page_number = request.GET.get("page") or 1
    paginator = Paginator(movements, 10)

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "Paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "movement_list.html", context)


@login_required
@require_http_methods(["GET"])
def movement_detail(request: HttpRequest, id: int) -> HttpResponse:
    """Renders a page with transaction details.

    Args:
        request (HttpRequest): Django request object.
        id (int): Unique transaction identifier.

    GET:
        Renders the screen with transaction data.

    Returns:
        HttpResponse: Detail page.
    """

    movement = get_object_or_404(Movement, id=id)

    context = {"movement": movement}
    return render(request, "movement_detail.html", context)


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def movement_delete(request: HttpRequest, id: int) -> HttpResponse:
    """Displays and processes the deletion of the transaction.

    Args:
        request (HttpRequest): Django request object.
        id (int): unique identifier of the transaction.

    GET:
        Renders the delete transaction screen requesting a password.

    POST:
        Validates the password:
            - If valid, deletes the transaction from the database with a success message.
            - If invalid, redirects to the password entry page with an error message.

    Returns:
        HttpResponse: Transaction deletion page (invalid password).
        HttpResponseRedirect: Redirect to the transaction list page (valid POST).
    """

    movement = get_object_or_404(Movement, id=id)
    context = {"movement": movement}

    if request.method == "GET":
        return render(request, "movement_delete.html", context)

    password = request.POST.get("password")

    if not request.user.check_password(password):
        messages.error(request, _("The password you entered is incorrect!"))
        return render(request, "movement_delete.html", context)

    movement.delete()

    messages.success(request, _("Movement successfully deleted!"))
    return redirect("movement_list")


# Review this
@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def report(request: HttpRequest) -> HttpResponse:
    """Creates a report of transactions for a specific period.

    Args:
        request (HttpRequest): Django request object.

    GET:
        Renders the report page.

    POST:
        Validates the entered period:
            - If valid, generates a report based on a specific period.
            - If invalid, returns to the report page with an error message.

    Returns:
        HttpRequest: Report generation page (invalid date).
        HttpsResponseRedirect: PDF of the report (valid POST).
    """

    if request.method == "GET":
        return render(request, "report.html")

    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    try:
        start_dt, end_dt = format_period(str(start_date), str(end_date))
    except ValidationError as e:
        messages.error(request, e.message)
        return render(request, "report.html", {"start_date": start_date, "end_date": end_date})

    # prefetch_related to perform only one search for all data that meets the filter criteria
    movements = (
        Movement.objects.filter(date__range=(start_dt, end_dt))
        .prefetch_related("ingredients", "products")
        .order_by("-date")
    )

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt=_("Movement Report"), ln=True, align="C")
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, _("Period: %(s_dt)s to %(e_dt)s") % {"s_dt": start_date, "e_dt": end_date}, ln=True, align="C")
    pdf.ln(5)

    total_in = 0
    total_out = 0

    for movement in movements:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{movement.get_type_display()} - {movement.date.strftime('%d/%m/%Y %H:%M')}", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 8, _("Responsible: %(user)s") % {"user": movement.user}, ln=True)
        pdf.cell(0, 8, _("Total value: $ %(value)s") % {"value": number_format(movement.value, 2)}, ln=True,)

        pdf.ln(2)
        if movement.type == "in":
            total_in += movement.value
            pdf.set_font("Arial", "B", 10)
            pdf.cell(80, 8, _("Name"), border=1)
            pdf.cell(40, 8, _("Quantity"), border=1)
            pdf.cell(40, 8, _("Price"), border=1)
            pdf.ln()

            for ing in movement.ingredients.all():
                pdf.set_font("Arial", size=10)
                pdf.cell(80, 8, ing.name, border=1)
                pdf.cell(40, 8, f"{ing.quantity_display} {ing.get_measure_display()}", border=1)
                pdf.cell(40, 8, _("$ %(price)s") % {"price": number_format(ing.price, 2)}, border=1)
                pdf.ln()
        else:
            total_out += movement.value
            pdf.set_font("Arial", "B", 10)
            pdf.cell(80, 8, _("Name"), border=1)
            pdf.cell(40, 8, _("Quantity"), border=1)
            pdf.cell(40, 8, _("Price"), border=1)
            pdf.ln()

            for prod in movement.products.all():
                pdf.set_font("Arial", size=10)
                pdf.cell(80, 8, prod.name, border=1)
                pdf.cell(40, 8, f"{prod.quantity}", border=1)
                pdf.cell(40, 8, _("$ %(price)s") % {"price": number_format(prod.price, 2)}, border=1)
                pdf.ln()

        pdf.ln(5)  # space between movements

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, _("Finantial Resume"), ln=True)

    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, _("Total Inflow: $ %(t_in)s") % {"t_in": number_format(total_in, 2)}, ln=True)
    pdf.cell(0, 8, _("Total Outflow: $ %(t_out)s") % {"t_out": number_format(total_out, 2)}, ln=True)
    pdf.cell(0, 8, _("Total Balance: $ %(tt)s") % {"tt": number_format(total_out - total_in, 2)}, ln=True)

    # Returning the PDF as an HTTP response
    response = HttpResponse(bytes(pdf.output(dest="S")), content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=relatorio.pdf"
    return response

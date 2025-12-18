from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import set_language

from .views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("schema-viewer/", include("schema_viewer.urls")),
    path("", home, name="home"),
    path("accounts/", include("accounts.urls"), name="accounts"),
    path("movements/", include("movements.urls"), name="movements"),
    path("stock/", include("stock.urls"), name="stock"),
    path("__reload__/", include("django_browser_reload.urls")),
    path('i18n/', include('django.conf.urls.i18n')),
]

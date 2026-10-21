from django.contrib import admin
from django.urls import include, path

# This list serves to route all incoming API requests to their respective application modules.
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/inventory/", include("apps.inventory.urls")),
    path("api/v1/reservations/", include("apps.reservations.urls")),
]
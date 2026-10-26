
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),

    # Registration, Login und Profile
    path("api/", include("auth_app.api.urls")),

    # Angebote und Angebotspakete
    path("api/", include("offers_app.api.urls")),

    # Bestellungen
    path("api/", include("orders_app.api.urls")),
]

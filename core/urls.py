
from django.contrib import admin
from django.urls import include, path

from .views import BaseInfoView


urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/base-info/", BaseInfoView.as_view()),

    path("api/", include("auth_app.api.urls")),
    path("api/", include("offers_app.api.urls")),
    path("api/", include("orders_app.api.urls")),
    path("api/", include("reviews_app.api.urls")),
]

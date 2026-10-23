
from django.urls import path

from .views import OfferDetailView, OfferListCreateView


urlpatterns = [
    path("offers/", OfferListCreateView.as_view()),
    path("offers/<int:pk>/", OfferDetailView.as_view()),
]

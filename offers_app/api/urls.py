
from django.urls import path

from .views import (
    OfferDetailSingleView,
    OfferDetailView,
    OfferListCreateView,
)


urlpatterns = [
    path(
        "offers/",
        OfferListCreateView.as_view()
    ),
    path(
        "offers/<int:pk>/",
        OfferDetailView.as_view()
    ),
    path(
        "offerdetails/<int:pk>/",
        OfferDetailSingleView.as_view()
    ),
]


from django.urls import path

from .views import ReviewDetailView, ReviewListCreateView


urlpatterns = [
    path(
        "reviews/",
        ReviewListCreateView.as_view()
    ),
    path(
        "reviews/<int:pk>/",
        ReviewDetailView.as_view()
    ),
]

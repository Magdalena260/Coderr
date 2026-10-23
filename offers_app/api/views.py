
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from offers_app.models import Offer

from .permissions import IsBusinessUser, IsOfferOwner
from .serializers import OfferSerializer


class OfferListCreateView(generics.ListCreateAPIView):
    queryset = Offer.objects.select_related(
        "user"
    ).prefetch_related("details")
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsBusinessUser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.select_related(
        "user"
    ).prefetch_related("details")
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated, IsOfferOwner]
    http_method_names = [
        "get", "patch", "delete", "head", "options"
    ]

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOfferOwner()]

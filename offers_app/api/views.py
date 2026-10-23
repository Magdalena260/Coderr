
from django.db.models import Min
from rest_framework import generics, serializers
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

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        max_price = self.request.query_params.get("max_price")

        if search:
            queryset = queryset.filter(
                title__icontains=search
            )

        if max_price is not None:
            try:
                price = int(max_price)
            except ValueError:
                raise serializers.ValidationError({
                    "max_price": "Must be a whole number."
                })

            if price < 0:
                raise serializers.ValidationError({
                    "max_price": "Must be zero or greater."
                })

            queryset = queryset.annotate(
                lowest_price=Min("details__price")
            ).filter(lowest_price__lte=price)

        return queryset


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

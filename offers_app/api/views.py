
from django.db.models import Min
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated

from offers_app.models import Offer, OfferDetail

from .pagination import OfferPagination
from .permissions import IsBusinessUser, IsOfferOwner
from .serializers import OfferDetailSerializer, OfferSerializer


class OfferListCreateView(generics.ListCreateAPIView):
    queryset = Offer.objects.select_related(
        "user"
    ).prefetch_related("details").order_by("id")

    serializer_class = OfferSerializer
    pagination_class = OfferPagination
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsBusinessUser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        search = params.get("search")
        max_price = params.get("max_price")
        max_delivery_time = params.get("max_delivery_time")
        creator_id = params.get("creator_id")
        ordering = params.get("ordering")

        if search:
            queryset = queryset.filter(
                title__icontains=search
            )

        if creator_id is not None:
            user_id = self.parse_number(
                creator_id, "creator_id"
            )
            queryset = queryset.filter(user_id=user_id)

        if max_price is not None or ordering in ["price", "-price"]:
            queryset = queryset.annotate(
                lowest_price=Min("details__price")
            )

        if max_price is not None:
            price = self.parse_number(max_price, "max_price")
            queryset = queryset.filter(lowest_price__lte=price)

        if max_delivery_time is not None:
            days = self.parse_number(
                max_delivery_time, "max_delivery_time"
            )
            queryset = queryset.annotate(
                shortest_delivery=Min(
                    "details__delivery_time_in_days"
                )
            ).filter(shortest_delivery__lte=days)

        if ordering is not None:
            if ordering not in ["price", "-price"]:
                raise serializers.ValidationError({
                    "ordering": "Use price or -price."
                })

            field = "lowest_price"
            if ordering == "-price":
                field = "-lowest_price"

            queryset = queryset.order_by(field, "id")

        return queryset

    def parse_number(self, value, field):
        try:
            number = int(value)
        except ValueError:
            raise serializers.ValidationError({
                field: "Must be a whole number."
            })

        if number < 0:
            raise serializers.ValidationError({
                field: "Must be zero or greater."
            })

        return number


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


class OfferDetailSingleView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.select_related("offer")
    serializer_class = OfferDetailSerializer
    permission_classes = [AllowAny]

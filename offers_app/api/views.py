
from decimal import Decimal, InvalidOperation

from django.db.models import Min, Q
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

    PRICE_ORDERINGS = (
        "min_price", "-min_price", "price", "-price"
    )

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsBusinessUser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        queryset = self._apply_search(queryset, params.get("search"))
        queryset = self._apply_creator(queryset, params.get("creator_id"))
        queryset = self._apply_price_filters(queryset, params)
        queryset = self._apply_delivery_filter(
            queryset, params.get("max_delivery_time")
        )
        return self._apply_ordering(queryset, params.get("ordering"))

    def _apply_search(self, queryset, search):
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
            )
        return queryset

    def _apply_creator(self, queryset, creator_id):
        if not creator_id:
            return queryset
        user_id = self._parse_integer(creator_id, "creator_id")
        return queryset.filter(user_id=user_id)

    def _needs_price_annotation(self, params):
        has_min = bool(params.get("min_price"))
        has_max = bool(params.get("max_price"))
        ordering = params.get("ordering")
        return has_min or has_max or ordering in self.PRICE_ORDERINGS

    def _apply_price_filters(self, queryset, params):
        if not self._needs_price_annotation(params):
            return queryset
        queryset = queryset.annotate(
            lowest_price=Min("details__price")
        )
        queryset = self._filter_price_bound(
            queryset, params, "min_price", "gte"
        )
        return self._filter_price_bound(
            queryset, params, "max_price", "lte"
        )

    def _filter_price_bound(self, queryset, params, name, lookup):
        raw_value = params.get(name)
        if not raw_value:
            return queryset
        value = self._parse_price(raw_value, name)
        return queryset.filter(
            **{f"lowest_price__{lookup}": value}
        )

    def _apply_delivery_filter(self, queryset, raw_value):
        if not raw_value:
            return queryset
        days = self._parse_integer(raw_value, "max_delivery_time")
        return queryset.annotate(
            shortest_delivery=Min("details__delivery_time_in_days")
        ).filter(shortest_delivery__lte=days)

    def _apply_ordering(self, queryset, ordering):
        if not ordering:
            return queryset
        fields = {
            "min_price": "lowest_price",
            "-min_price": "-lowest_price",
            "price": "lowest_price",
            "-price": "-lowest_price",
            "updated_at": "updated_at",
            "-updated_at": "-updated_at",
        }
        if ordering not in fields:
            raise serializers.ValidationError({
                "ordering": "Invalid ordering field."
            })
        return queryset.order_by(fields[ordering], "id")

    def _parse_integer(self, value, field):
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

    def _parse_price(self, value, field):
        try:
            number = Decimal(value)
        except (InvalidOperation, ValueError):
            raise serializers.ValidationError({
                field: "Must be a valid number."
            })
        if not number.is_finite() or number < 0:
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
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOfferOwner()]


class OfferDetailSingleView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.select_related("offer")
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]

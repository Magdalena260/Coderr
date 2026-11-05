
from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=OfferDetail.objects.select_related("offer__user"),
        source="offer_detail",
        write_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "offer_detail",
            "offer_detail_id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "customer_user",
            "business_user",
            "offer_detail",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context.get("request")
        self._validate_customer(request)
        detail = attrs["offer_detail"]
        if detail.offer.user_id == request.user.id:
            raise serializers.ValidationError(
                "You cannot order your own offer."
            )
        return attrs

    def _validate_customer(self, request):
        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required."
            )
        profile = getattr(request.user, "profile", None)
        if profile is None or profile.type != "customer":
            raise serializers.ValidationError(
                "Only customers can create orders."
            )

    def create(self, validated_data):
        detail = validated_data["offer_detail"]
        customer = self.context["request"].user
        return Order.objects.create(
            customer_user=customer,
            business_user=detail.offer.user,
            offer_detail=detail,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=list(detail.features),
            offer_type=detail.offer_type,
        )

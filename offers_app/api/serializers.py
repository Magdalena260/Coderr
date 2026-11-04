
from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id"]


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        path = f"/api/offerdetails/{obj.id}/"
        request = self.context.get("request")

        if request is not None:
            return request.build_absolute_uri(path)

        return path


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        details = attrs.get("details")

        if self.instance is None:
            self._validate_create_details(details)
        elif details is not None:
            self._validate_update_details(details)

        return attrs

    def _validate_create_details(self, details):
        if details is None:
            raise serializers.ValidationError({
                "details": "Three packages are required."
            })

        types = [d.get("offer_type") for d in details]
        required = {"basic", "standard", "premium"}

        if len(types) != 3 or set(types) != required:
            raise serializers.ValidationError({
                "details": (
                    "Exactly one basic, standard and "
                    "premium package is required."
                )
            })

    def _validate_update_details(self, details):
        types = [d.get("offer_type") for d in details]

        if None in types or len(types) != len(set(types)):
            raise serializers.ValidationError({
                "details": (
                    "Each package needs a unique offer_type."
                )
            })

    def _get_detail_links(self, instance):
        serializer = OfferDetailLinkSerializer(
            instance.details.all(),
            many=True,
            context=self.context
        )
        return serializer.data

    def _add_statistics(self, data, instance):
        details = list(instance.details.all())

        data["min_price"] = min(
            (detail.price for detail in details),
            default=None
        )
        data["min_delivery_time"] = min(
            (detail.delivery_time_in_days for detail in details),
            default=None
        )

    def _get_user_details(self, instance):
        user = instance.user
        profile = getattr(user, "profile", None)

        return {
            "first_name": getattr(
                profile, "first_name", user.first_name
            ),
            "last_name": getattr(
                profile, "last_name", user.last_name
            ),
            "username": user.username,
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        if request is None or request.method != "GET":
            return data

        data["details"] = self._get_detail_links(instance)
        self._add_statistics(data, instance)

        if isinstance(self.parent, serializers.ListSerializer):
            data["user_details"] = self._get_user_details(instance)

        return data

    @transaction.atomic
    def create(self, validated_data):
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(
                offer=offer,
                **detail_data
            )

        return offer

    def _update_single_detail(self, instance, detail_data):
        detail_type = detail_data.pop("offer_type")

        try:
            detail = instance.details.get(
                offer_type=detail_type
            )
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError({
                "details": "Package does not exist."
            })

        for field, value in detail_data.items():
            setattr(detail, field, value)

        detail.save()

    @transaction.atomic
    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        if details_data is not None:
            for detail_data in details_data:
                self._update_single_detail(instance, detail_data)

        return instance


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
            if details is None:
                raise serializers.ValidationError({
                    "details": "Three packages are required."
                })

            types = [d["offer_type"] for d in details]
            required = {"basic", "standard", "premium"}

            if len(types) != 3 or set(types) != required:
                raise serializers.ValidationError({
                    "details": (
                        "Exactly one basic, standard and "
                        "premium package is required."
                    )
                })

        elif details is not None:
            types = [d.get("offer_type") for d in details]

            if None in types or len(types) != len(set(types)):
                raise serializers.ValidationError({
                    "details": (
                        "Each package needs a unique offer_type."
                    )
                })

        return attrs

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

    @transaction.atomic
    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        if details_data is not None:
            for detail_data in details_data:
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

        return instance

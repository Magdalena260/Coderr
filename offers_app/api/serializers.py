
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
    details = OfferDetailSerializer(many=True)

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

    def validate_details(self, value):
        types = [detail["offer_type"] for detail in value]
        required = {"basic", "standard", "premium"}

        if not types or len(types) != len(set(types)):
            raise serializers.ValidationError(
                "Offer types must be unique."
            )

        if not set(types).issubset(required):
            raise serializers.ValidationError(
                "Invalid offer type."
            )

        if not self.partial and set(types) != required:
            raise serializers.ValidationError(
                "Exactly one basic, standard and premium detail is required."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(
                offer=offer, **detail_data
            )

        return offer

    @transaction.atomic
    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)
        instance = super().update(instance, validated_data)

        if details_data is not None:
            for detail_data in details_data:
                detail_type = detail_data.pop("offer_type")
                detail = instance.details.get(offer_type=detail_type)

                for field, value in detail_data.items():
                    setattr(detail, field, value)

                detail.save()

        return instance

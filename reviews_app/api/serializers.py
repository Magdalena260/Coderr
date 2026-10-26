
from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews_app.models import Review


User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reviewer",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required."
            )

        if self.instance is not None:
            if "business_user" in attrs:
                raise serializers.ValidationError({
                    "business_user": "Cannot change the business user."
                })
            return attrs

        business_user = attrs["business_user"]

        if business_user == request.user:
            raise serializers.ValidationError(
                "You cannot review yourself."
            )

        if Review.objects.filter(
            business_user=business_user,
            reviewer=request.user
        ).exists():
            raise serializers.ValidationError(
                "You have already reviewed this business user."
            )

        return attrs

    def create(self, validated_data):
        return Review.objects.create(
            reviewer=self.context["request"].user,
            **validated_data
        )

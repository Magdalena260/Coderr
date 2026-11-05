
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from auth_app.models import Profile


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False
    )
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=Profile.USER_TYPES,
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "repeated_password",
            "type",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError({
                "repeated_password": "Passwords do not match."
            })
        if User.objects.filter(
            email__iexact=attrs["email"]
        ).exists():
            raise serializers.ValidationError({
                "email": "Email already registered."
            })
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user_type = validated_data.pop("type")
        validated_data.pop("repeated_password")
        password = validated_data.pop("password")
        user = User.objects.create_user(
            password=password, **validated_data
        )
        Profile.objects.create(user=user, type=user_type)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username", read_only=True
    )
    first_name = serializers.CharField(
        source="user.first_name",
        required=False,
        allow_blank=True
    )
    last_name = serializers.CharField(
        source="user.last_name",
        required=False,
        allow_blank=True
    )
    email = serializers.EmailField(
        source="user.email",
        required=False
    )

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "type",
            "created_at",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        for field, value in user_data.items():
            setattr(instance.user, field, value)

        if user_data:
            instance.user.save(
                update_fields=list(user_data)
            )

        return super().update(instance, validated_data)


class BusinessProfileSerializer(ProfileSerializer):
    class Meta(ProfileSerializer.Meta):
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]


class CustomerProfileSerializer(ProfileSerializer):
    class Meta(ProfileSerializer.Meta):
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "type",
        ]

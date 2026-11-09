
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APITestCase

from auth_app.models import Profile
from reviews_app.api.serializers import ReviewSerializer
from reviews_app.models import Review


User = get_user_model()


class ReviewSerializerTests(APITestCase):

    def setUp(self):
        self.reviewer = self.create_user(
            "review_customer", "customer"
        )
        self.business = self.create_user(
            "review_business", "business"
        )
        self.other_business = self.create_user(
            "other_business", "business"
        )

    def create_user(self, username, user_type):
        user = User.objects.create_user(
            username=username,
            password="TestPassword123!"
        )
        Profile.objects.create(user=user, type=user_type)
        return user

    def valid_data(self):
        return {
            "business_user": self.business.id,
            "rating": 5,
            "description": "Very good service."
        }

    def make_serializer(self, data, instance=None, user=None):
        if user is None:
            user = self.reviewer

        request = SimpleNamespace(user=user)

        return ReviewSerializer(
            instance,
            data=data,
            partial=instance is not None,
            context={"request": request}
        )

    def create_review(self):
        return Review.objects.create(
            reviewer=self.reviewer,
            business_user=self.business,
            rating=5,
            description="Good service."
        )

    def test_valid_review_can_be_created(self):
        serializer = self.make_serializer(
            self.valid_data()
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        review = serializer.save()

        self.assertEqual(review.reviewer, self.reviewer)
        self.assertEqual(review.business_user, self.business)

    def test_user_cannot_review_themselves(self):
        serializer = self.make_serializer(
            self.valid_data(),
            user=self.business
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_duplicate_review_is_rejected(self):
        self.create_review()

        serializer = self.make_serializer(
            self.valid_data()
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_business_user_cannot_be_changed(self):
        review = self.create_review()

        serializer = self.make_serializer(
            {"business_user": self.other_business.id},
            instance=review
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("business_user", serializer.errors)

    def test_rating_can_be_updated(self):
        review = self.create_review()

        serializer = self.make_serializer(
            {"rating": 4},
            instance=review
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        review.refresh_from_db()

        self.assertEqual(review.rating, 4)

    def test_anonymous_user_is_rejected(self):
        serializer = self.make_serializer(
            self.valid_data(),
            user=AnonymousUser()
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_missing_request_is_rejected(self):
        serializer = ReviewSerializer(
            data=self.valid_data()
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_unknown_business_user_is_rejected(self):
        data = self.valid_data()
        data["business_user"] = 9999999

        serializer = self.make_serializer(data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("business_user", serializer.errors)

    def test_customer_cannot_be_reviewed(self):
        data = self.valid_data()
        data["business_user"] = self.reviewer.id

        serializer = self.make_serializer(data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("business_user", serializer.errors)

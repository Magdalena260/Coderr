
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from reviews_app.models import Review


class ReviewPermissionTests(APITestCase):

    def setUp(self):
        User = get_user_model()

        self.customer = User.objects.create_user(
            username="test_customer",
            password="TestPassword123!"
        )

        self.business = User.objects.create_user(
            username="test_business",
            password="TestPassword123!"
        )

        self.review = Review.objects.create(
            reviewer=self.customer,
            business_user=self.business,
            rating=4,
            description="Tolles Logo!"
        )

        self.url = f"/api/reviews/{self.review.id}/"

    def test_anonymous_cannot_delete_review(self):
        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        self.assertTrue(
            Review.objects.filter(pk=self.review.pk).exists()
        )

    def test_business_cannot_delete_review(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertTrue(
            Review.objects.filter(pk=self.review.pk).exists()
        )

    def test_author_can_delete_review(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Review.objects.filter(pk=self.review.pk).exists()
        )

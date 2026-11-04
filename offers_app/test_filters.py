
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail


User = get_user_model()


class OfferFilterTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="filter_owner",
            password="TestPassword123!"
        )
        self.other = User.objects.create_user(
            username="filter_other",
            password="TestPassword123!"
        )
        self.cheap = self.make_offer(
            self.owner, "Logo Design", "Simple logo", 50, 3
        )
        self.expensive = self.make_offer(
            self.other, "Website Design",
            "Creative website illustration", 150, 10
        )

    def make_offer(self, user, title, description, price, days):
        offer = Offer.objects.create(
            user=user, title=title, description=description
        )
        OfferDetail.objects.create(
            offer=offer, title="Basic", revisions=1,
            delivery_time_in_days=days, price=price,
            features=["Design"], offer_type="basic"
        )
        return offer

    def test_min_price_filter(self):
        response = self.client.get(
            "/api/offers/?min_price=100"
        )
        ids = [item["id"] for item in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ids, [self.expensive.id])

    def test_search_in_description(self):
        response = self.client.get(
            "/api/offers/?search=illustration"
        )
        ids = [item["id"] for item in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ids, [self.expensive.id])

    def test_creator_id_filter(self):
        response = self.client.get(
            f"/api/offers/?creator_id={self.owner.id}"
        )
        ids = [item["id"] for item in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ids, [self.cheap.id])

    def test_ordering_by_min_price(self):
        response = self.client.get(
            "/api/offers/?ordering=-min_price"
        )
        ids = [item["id"] for item in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ids, [self.expensive.id, self.cheap.id]
        )

    def test_ordering_by_updated_at(self):
        old_date = timezone.now() - timedelta(days=2)
        Offer.objects.filter(pk=self.cheap.pk).update(
            updated_at=old_date
        )
        response = self.client.get(
            "/api/offers/?ordering=updated_at"
        )
        ids = [item["id"] for item in response.data["results"]]

        self.assertEqual(ids, [self.cheap.id, self.expensive.id])

    def test_invalid_min_price(self):
        response = self.client.get(
            "/api/offers/?min_price=abc"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

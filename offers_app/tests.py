
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail


User = get_user_model()


class OfferTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="offer_owner",
            password="TestPassword123!"
        )
        self.other_user = User.objects.create_user(
            username="other_user",
            password="TestPassword123!"
        )

        self.offer = Offer.objects.create(
            user=self.owner,
            title="Logo Design",
            description="Professional logo design"
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Logo",
            revisions=2,
            delivery_time_in_days=3,
            price=75,
            features=["Logo", "PNG"],
            offer_type="basic"
        )

        self.second_offer = Offer.objects.create(
            user=self.other_user,
            title="Website Design",
            description="Professional website design"
        )
        OfferDetail.objects.create(
            offer=self.second_offer,
            title="Basic Website",
            revisions=1,
            delivery_time_in_days=10,
            price=250,
            features=["Website"],
            offer_type="basic"
        )

    def test_offers_list_is_public(self):
        response = self.client.get("/api/offers/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_invalid_max_price(self):
        response = self.client.get(
            "/api/offers/?max_price=abc"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_negative_delivery_time(self):
        response = self.client.get(
            "/api/offers/?max_delivery_time=-5"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_invalid_ordering(self):
        response = self.client.get(
            "/api/offers/?ordering=title"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_offer_detail_is_public(self):
        response = self.client.get(
            f"/api/offers/{self.offer.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_single_offer_detail_is_public(self):
        response = self.client.get(
            f"/api/offerdetails/{self.detail.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_search_filter(self):
        response = self.client.get(
            "/api/offers/?search=Logo"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            len(response.data["results"]),
            1
        )

    def test_max_price_filter(self):
        response = self.client.get(
            "/api/offers/?max_price=100"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            len(response.data["results"]),
            1
        )

    def test_delivery_time_filter(self):
        response = self.client.get(
            "/api/offers/?max_delivery_time=5"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            len(response.data["results"]),
            1
        )

    def test_unauthenticated_cannot_create_offer(self):
        response = self.client.post(
            "/api/offers/",
            {"title": "New Offer"},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_other_user_cannot_edit_offer(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.patch(
            f"/api/offers/{self.offer.id}/",
            {"title": "Changed Title"},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_owner_can_delete_offer(self):
        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.delete(
            f"/api/offers/{self.offer.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )
        self.assertFalse(
            Offer.objects.filter(
                id=self.offer.id
            ).exists()
        )

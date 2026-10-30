
from rest_framework import status
from rest_framework.test import APITestCase


class OfferTests(APITestCase):

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


from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail


User = get_user_model()


class OfferResponseTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_designer",
            password="TestPassword123!"
        )

        self.offer = Offer.objects.create(
            user=self.user,
            title="Design Package",
            description="Creative design services"
        )

        for offer_type, price, days in [
            ("basic", 50, 3),
            ("standard", 100, 5),
            ("premium", 150, 7),
        ]:
            OfferDetail.objects.create(
                offer=self.offer,
                title=offer_type.title(),
                revisions=1,
                delivery_time_in_days=days,
                price=price,
                features=["Design"],
                offer_type=offer_type
            )

    def test_offer_list_response_fields(self):
        response = self.client.get("/api/offers/")

        self.assertEqual(response.status_code, 200)
        offer = response.data["results"][0]

        self.assertEqual(offer["min_price"], 50)
        self.assertEqual(offer["min_delivery_time"], 3)
        self.assertEqual(len(offer["details"]), 3)
        self.assertIn("user_details", offer)
        self.assertEqual(
            offer["user_details"]["username"],
            "test_designer"
        )

    def test_offer_detail_response_fields(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f"/api/offers/{self.offer.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(response.data["min_price"], 50)
        self.assertEqual(response.data["min_delivery_time"], 3)

        for detail in response.data["details"]:
            self.assertIn("id", detail)
            self.assertIn("url", detail)
            self.assertIn("/api/offerdetails/", detail["url"])

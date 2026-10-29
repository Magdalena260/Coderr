
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import Profile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order


class OrderTests(APITestCase):

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

        Profile.objects.create(
            user=self.customer,
            type="customer"
        )

        Profile.objects.create(
            user=self.business,
            type="business"
        )

        self.offer = Offer.objects.create(
            user=self.business,
            title="Logo Design",
            description="Ein individuelles Logo"
        )

        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Logo",
            revisions=1,
            delivery_time_in_days=5,
            price=75,
            features=["Logo", "PNG Datei"],
            offer_type="basic"
        )

        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            offer_detail=self.detail,
            title=self.detail.title,
            revisions=self.detail.revisions,
            delivery_time_in_days=self.detail.delivery_time_in_days,
            price=self.detail.price,
            features=self.detail.features,
            offer_type=self.detail.offer_type
        )

        self.url = f"/api/orders/{self.order.id}/"

    def test_anonymous_cannot_view_orders(self):
        response = self.client.get("/api/orders/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_customer_can_view_order(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["price"],
            75
        )

    def test_customer_cannot_update_status(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.patch(
            self.url,
            {"status": "completed"},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            "in_progress"
        )

    def test_business_can_complete_order(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.patch(
            self.url,
            {"status": "completed"},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            "completed"
        )

    def test_customer_can_create_order(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            "/api/orders/",
            {"offer_detail_id": self.detail.id},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Order.objects.count(),
            2
        )

    def test_completed_order_count(self):
        self.order.status = "completed"
        self.order.save()

        response = self.client.get(
            f"/api/completed-order-count/{self.business.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["completed_order_count"],
            1
        )

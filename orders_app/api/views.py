
from django.db.models import Q

from rest_framework import generics, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders_app.models import Order
from .serializers import OrderSerializer


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return Order.objects.filter(
            Q(customer_user=user) |
            Q(business_user=user)
        ).select_related(
            "customer_user",
            "business_user",
            "offer_detail"
        ).order_by("-created_at")


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "get", "patch", "delete", "head", "options"
    ]

    def get_queryset(self):
        queryset = Order.objects.select_related(
            "customer_user",
            "business_user",
            "offer_detail"
        )

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(
            Q(customer_user=self.request.user) |
            Q(business_user=self.request.user)
        )

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return OrderStatusSerializer

        return OrderSerializer

    def patch(self, request, *args, **kwargs):
        order = self.get_object()

        if order.business_user_id != request.user.id:
            raise PermissionDenied(
                "Only the business user can update this order."
            )

        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied(
                "Only staff can delete orders."
            )

        return super().delete(request, *args, **kwargs)


class OrderCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, business_user_id):
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status="in_progress"
        ).count()

        return Response({"order_count": count})


class CompletedOrderCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, business_user_id):
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status="completed"
        ).count()

        return Response({"completed_order_count": count})

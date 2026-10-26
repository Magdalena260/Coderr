
from rest_framework import generics, permissions

from reviews_app.models import Review
from .serializers import ReviewSerializer


class IsReviewAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.reviewer_id == request.user.id


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    def get_queryset(self):
        queryset = Review.objects.select_related(
            "business_user",
            "reviewer"
        ).order_by("-created_at")

        business_id = self.request.query_params.get(
            "business_user_id"
        )
        reviewer_id = self.request.query_params.get(
            "reviewer_id"
        )

        if business_id:
            queryset = queryset.filter(
                business_user_id=business_id
            )

        if reviewer_id:
            queryset = queryset.filter(
                reviewer_id=reviewer_id
            )

        return queryset


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsReviewAuthor,
    ]
    http_method_names = [
        "get", "patch", "delete", "head", "options"
    ]

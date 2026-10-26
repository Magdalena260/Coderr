
from django.db.models import Avg
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import Profile
from offers_app.models import Offer
from reviews_app.models import Review


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        average_rating = Review.objects.aggregate(
            average=Avg("rating")
        )["average"]

        return Response({
            "review_count": Review.objects.count(),
            "average_rating": round(average_rating or 0, 2),
            "business_profile_count": Profile.objects.filter(
                type="business"
            ).count(),
            "offer_count": Offer.objects.count(),
        })

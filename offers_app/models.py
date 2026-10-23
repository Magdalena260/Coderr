
from django.conf import settings
from django.db import models


class Offer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="offers"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="offers/",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class OfferDetail(models.Model):
    OFFER_TYPES = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="details"
    )
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField(default=0)
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    features = models.JSONField(default=list)
    offer_type = models.CharField(
        max_length=10,
        choices=OFFER_TYPES
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["offer", "offer_type"],
                name="unique_offer_type_per_offer"
            )
        ]

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"

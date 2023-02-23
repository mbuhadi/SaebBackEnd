from rest_framework import serializers
from dealer.models import Dealer
from django.core.validators import RegexValidator


class DealerSerializer(serializers.ModelSerializer):
    carry_over = serializers.IntegerField(source="get_carry_over", read_only=True)
    phone = serializers.RegexField(regex=r"\d{8}")

    class Meta:
        model = Dealer
        fields = (
            "name",
            "phone",
            "office",
            "credit",
            "carry_over",
            "post_count",
            "remaining",
        )
        read_only = (
            "phone",
            "office",
            "credit",
            "carry_over",
            "post_count",
            "remaining",
        )


class DealerSummerySerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        validators=[
            RegexValidator(r"^\d{8}$", "phone must be 8 digits"),
        ],
    )

    class Meta:
        model = Dealer
        fields = (
            "name",
            "phone",
            "office",
        )

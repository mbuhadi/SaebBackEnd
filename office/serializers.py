from dealer.serializers import DealerSerializer
from rest_framework import serializers
from .models import Office

from django.core.validators import RegexValidator
from dealer.serializers import DealerSummerySerializer


class OfficeSerializer(serializers.ModelSerializer):
    dealers = DealerSummerySerializer(many=True)
    owner = DealerSummerySerializer()
    image = serializers.SerializerMethodField()

    def get_image(self, office):
        request = self.context.get("request")
        if office.image:
            image = office.image.url
            return request.build_absolute_uri(image)

    class Meta:
        model = Office
        fields = (
            "id",
            "name_ar",
            "name_en",
            "image",
            "created",
            "owner",
            "dealers",
        )
        read_only = ("id",)


class OfficeSummerySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, office):
        request = self.context.get("request")
        if office.image:
            image = office.image.url
            return request.build_absolute_uri(image)

    class Meta:
        model = Office
        fields = (
            "id",
            "name_ar",
            "name_en",
            "image",
            "owner",
        )
        read_only = ("id",)

from office.serializers import OfficeSummerySerializer
from dealer.serializers import DealerSummerySerializer
from django.core.validators import RegexValidator
from rest_framework import serializers
from .models import Deal, PropertyOutlook, PropertyType, PropertyArea, Governorate
from dealer.models import Dealer


class GovernorateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Governorate
        fields = (
            "id",
            "name_en",
            "name_ar",
        )


class PropertyAreaSerializer(serializers.ModelSerializer):
    governorate = GovernorateSerializer()

    class Meta:
        model = PropertyArea
        fields = (
            "id",
            "governorate",
            "name_ar",
            "name_en",
        )


class PropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyType
        fields = (
            "id",
            "name_ar",
            "name_en",
        )


class PropertyOutlookSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyOutlook
        fields = (
            "id",
            "name_en",
            "name_ar",
        )


class DealSerializer(serializers.ModelSerializer):
    office = OfficeSummerySerializer(source="dealer.office", read_only=True)
    # created = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["dealer"] = DealerSummerySerializer(instance.dealer).data
        data["property_type"] = PropertyTypeSerializer(instance.property_type).data
        data["property_area"] = PropertyAreaSerializer(instance.property_area).data
        data["property_outlook"] = PropertyOutlookSerializer(
            instance.property_outlook
        ).data

        return data

    class Meta:
        model = Deal

        fields = (
            "id",
            "property_type",
            "property_area",
            "property_outlook",
            "description",
            "date_created",
            "office",
            "dealer",
        )
        read_only_fields = (
            "id",
            "date_created",
            "office",
        )

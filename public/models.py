from django.db import models
from django.db.models import Sum
from utility import get_today_indexed_date
from dealer.models import Dealer
from root.validators import validate_min_text


class PropertyType(models.Model):
    name_ar = models.CharField(max_length=20)
    name_en = models.CharField(max_length=20)

    def __str__(self):
        return self.name_en


class Governorate(models.Model):
    name_ar = models.CharField(max_length=20)
    name_en = models.CharField(max_length=20)

    class Meta:
        ordering = ["name_ar"]

    def __str__(self):
        return self.name_en


class PropertyArea(models.Model):
    governorate = models.ForeignKey(
        Governorate, on_delete=models.RESTRICT, related_name="area_governorate"
    )
    name_ar = models.CharField(max_length=20)
    name_en = models.CharField(max_length=20)

    def __str__(self):
        return self.name_en


class PropertyOutlook(models.Model):
    name_ar = models.CharField(max_length=20)
    name_en = models.CharField(max_length=20)

    def __str__(self):
        return self.name_en


class Deal(models.Model):
    property_type = models.ForeignKey(PropertyType, on_delete=models.RESTRICT)
    property_area = models.ForeignKey(PropertyArea, on_delete=models.RESTRICT)
    property_outlook = models.ForeignKey(PropertyOutlook, on_delete=models.RESTRICT)
    description = models.CharField(max_length=400, validators=[validate_min_text])
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name="deals")
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description

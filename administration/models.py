import datetime
from django.db import models
from django.db.models.fields import CharField, DateTimeField
from django.db.models.fields.related import OneToOneField
from rest_framework.fields import BooleanField
from dealer.models import Dealer
from utility import create_transaction_id
from unixtimestampfield.fields import UnixTimeStampField
import uuid
from utility import create_transaction_id
from public.models import PropertyType, PropertyArea, PropertyOutlook, Deal


class AdminUser(models.Model):
    dealer = models.OneToOneField(
        Dealer,
        on_delete=models.CASCADE,
        related_name="admin",
        null=True,
        blank=True,
    )
    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="admin_user",
    )

    is_admin = models.BooleanField(default=False)

    def has_permission(self, permission) -> bool:
        if self.is_admin:
            return True

        return self.role.has_permission(permission)

    def __str__(self):
        return self.dealer.phone


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    permissions = models.BigIntegerField()

    def has_permission(self, permission) -> bool:
        return self.permissions & permission == permission

    def __str__(self):
        return self.name


class Offer(models.Model):
    name_ar = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="offers/")
    price = models.IntegerField()
    credit = models.IntegerField()
    duration = models.IntegerField(default=1)

    def __str__(self):
        return str(self.id)


class Credit(models.Model):
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name="credits")
    amount = models.IntegerField()
    indexed_date = models.IntegerField(db_index=True)

    def __str__(self):
        return str(self.amount)


# featureS we purchased
class Purchase(models.Model):
    dealer = models.ForeignKey(
        Dealer, on_delete=models.CASCADE, related_name="dealer_purchases"
    )
    credit = models.IntegerField()
    date_fullfilled = models.DateTimeField(auto_now_add=True)
    # start_of_date_fullfilled = models.DateTimeField(default=)
    indexed_date = models.IntegerField()
    duration = models.IntegerField(default=1)

    def __str__(self):
        return str(self.id)


class CarryOver(models.Model):
    dealer = models.ForeignKey(
        Dealer, on_delete=models.CASCADE, related_name="carry_over"
    )
    amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    indexed_date = models.IntegerField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["dealer", "indexed_date"]),
        ]
        unique_together = [
            ["dealer", "indexed_date"],
        ]


class Transaction(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=100,
        unique=True,
    )
    offer = models.ForeignKey(
        Offer, on_delete=models.RESTRICT, related_name="transaction"
    )
    price = models.FloatField()
    date_issued = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=20, null=True, blank=True)
    method = models.CharField(max_length=100)
    purchase = models.OneToOneField(
        Purchase,
        on_delete=models.CASCADE,
        related_name="transaction",
        null=True,
        blank=True,
    )
    duration = models.IntegerField(default=1)
    redirect_destination = models.CharField(max_length=1000, default="home")
    date_fullfilled = models.DateTimeField(null=True, blank=True)
    indexed_date = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.id)


class Message(models.Model):
    result = models.CharField(max_length=10)
    msg_id = models.CharField(
        max_length=32,
        primary_key=True,
        unique=True,
        db_index=True,
    )
    numbers = models.CharField(max_length=10)
    points_charged = models.CharField(max_length=10)
    balance_after = models.CharField(max_length=10)
    UNIX_timestamp = UnixTimeStampField()
    indexed_date = models.IntegerField(db_index=True)
    msg = models.TextField()
    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.msg_id)


class Log(models.Model):
    time = models.DateTimeField(primary_key=True, auto_now_add=True)
    ip_address = models.CharField(max_length=30)
    is_dealer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    type_of_request = models.CharField(max_length=30)
    route_of_request = models.CharField(max_length=30)

    def __str__(self):
        return str(self.ip_address)


class DeletedDeal(models.Model):
    property_type = models.ForeignKey(PropertyType, on_delete=models.RESTRICT)
    property_area = models.ForeignKey(PropertyArea, on_delete=models.RESTRICT)
    property_outlook = models.ForeignKey(PropertyOutlook, on_delete=models.RESTRICT)
    description = models.CharField(max_length=500)
    dealer = models.ForeignKey(
        Dealer, on_delete=models.CASCADE, related_name="deleted_deals"
    )

    def __str__(self):
        return self.description


class DealLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)

    dealer = models.ForeignKey(
        Dealer, on_delete=models.CASCADE, related_name="logs", null=True, blank=True
    )

    deal = models.ForeignKey(
        Deal,
        on_delete=models.SET_NULL,
        related_name="logs",
        null=True,
        blank=True,
    )

    deleted_deal = models.ForeignKey(
        DeletedDeal,
        on_delete=models.RESTRICT,
        related_name="logs",
        blank=True,
        null=True,
    )

    indexed_date = models.IntegerField(db_index=True)

    def __str__(self):
        if self.deal:
            return str(self.deal.id) + " - " + str(self.date)
        else:
            return str(self.deleted_deal.id) + " - " + str(self.date)

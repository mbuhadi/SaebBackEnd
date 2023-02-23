from rest_framework import serializers
import administration.permissions as perms
from .models import AdminUser, Role, Purchase, Offer, Purchase, Transaction, Message


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    def get_permissions(self, obj):
        return {
            permission_name: obj.has_permission(permission_value)
            for permission_name, permission_value in perms.permissions_dict.items()
        }

    class Meta:
        model = Role
        fields = ("id", "name", "permissions")


class AdminUserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    def get_role(self, obj):
        return {
            permission_name: obj.has_permission(permission_value)
            for permission_name, permission_value in perms.permissions_dict.items()
        }

    class Meta:
        model = AdminUser
        fields = ("role",)


class OfferSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, office):
        request = self.context.get("request")
        if office.image:
            image = office.image.url
            return request.build_absolute_uri(image)
    class Meta:
        model = Offer
        fields = (
            "id",
            "name_ar",
            "name_en",
            "credit",
            "price",
            "image",
        )


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = (
            "dealer",  # call 1
            "credit",  # call 1 (directly)
            "date_fullfilled",
            "indexed_date",  # call 1
        )


class IncompleteTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("id", "offer", "price", "dealer", "status", "date_issued")


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"

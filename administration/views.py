from random import randint
import json, sys
import base64
from public.views import DealListAPIView
import re
from os import makedirs
from os.path import join, exists
from django.db.models.aggregates import Max
from rest_framework import permissions, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.files.base import ContentFile
from public.models import Deal, Dealer, PropertyArea, PropertyType, PropertyOutlook
from public.serializers import (
    DealSerializer,
    PropertyAreaSerializer,
    PropertyTypeSerializer,
    PropertyOutlookSerializer,
)
from dealer.serializers import DealerSerializer
from office.models import Office
from office.serializers import (
    OfficeSerializer,
)
from utility import get_today_indexed_date, create_reference_id, create_rndm
from utility2 import create_log, am_i_dealer, am_i_admin
from .serializers import (
    AdminUserSerializer,
    RoleSerializer,
    OfferSerializer,
    IncompleteTransactionSerializer,
    PurchaseSerializer,
    TransactionSerializer,
    MessageSerializer,
)
from . import permissions as perms
from .models import Role, Offer, Purchase, Transaction, Message
from rest_framework import generics
from django.http import JsonResponse
from requests import Request, Session
import requests
import json
from urllib.request import urlopen
import json
import pprint
from datetime import datetime
from root.paginators import DealPagination
import requests

# Permission
@api_view(["GET"])
def get_permissions(request):
    try:
        # create_log(
        #     request,
        #     am_i_dealer(request),
        #     am_i_admin(request),
        #     request.method,
        #     "get_permissions",
        # )
        return JsonResponse(
            AdminUserSerializer(request.user.dealer.admin).data["role"],
            status=status.HTTP_200_OK,
        )
    # pylint: disable=no-member
    except Dealer.admin.RelatedObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)


class SaebPermission(permissions.BasePermission):
    """
    Sets all methods to forbidden unless proper flag is set.
    get_permission, post_permission, patch_permission, and delete_permission
    saeb_sequential_permissions sets get to x1, post_permission to x2, patch_permission x3, and delete_permission to x4.
    """

    def has_permission(self, request, view):
        try:
            admin_user = request.user.dealer.admin
            blocked = []
            try:
                blocked = view.saeb_block
            except AttributeError:
                pass

            if request.method in blocked:
                return False

            try:
                if view.saeb_sequential_permissions:
                    view.get_permission = view.saeb_sequential_permissions
                    view.post_permission = view.saeb_sequential_permissions * 2
                    view.patch_permission = view.saeb_sequential_permissions * 3
                    view.delete_permission = view.saeb_sequential_permissions * 4
            except AttributeError:
                pass

            if request.method == "GET" and view.get_permission:
                return admin_user.has_permission(view.get_permission)
            elif request.method == "POST" and view.post_permission:
                return admin_user.has_permission(view.post_permission)
            elif request.method == "PATCH" and view.patch_permission:
                return admin_user.has_permission(view.patch_permission)
            elif request.method == "DELETE" and view.delete_permission:
                return admin_user.has_permission(view.delete_permission)

        # pylint: disable= no-member
        except Dealer.admin.RelatedObjectDoesNotExist:
            pass
        except AttributeError:
            pass
        return False


class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = (SaebPermission,)
    queryset = Role.objects.all().exclude(admin_user__is_admin=True)
    serializer_class = RoleSerializer
    saeb_sequential_permissions = perms.ROLE_VIEW

    def list(self, request, *args, **kwargs):
        # create_log(
        #     request,
        #     am_i_dealer(request),
        #     am_i_admin(request),
        #     self.request.method,
        #     "RoleViewSet-list",
        # )
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # create_log(
        #     request,
        #     am_i_dealer(request),
        #     am_i_admin(request),
        #     self.request.method,
        #     "RoleViewSet-create",
        # )
        value = 0
        body = json.loads(request.body)

        if not "name" in body:
            return Response("missing name field", status=status.HTTP_400_BAD_REQUEST)

        name = body["name"]
        del body["name"]
        for key in body:
            if not key in perms.permissions_dict:
                return Response(
                    "unknown field " + key, status=status.HTTP_400_BAD_REQUEST
                )

            if body[key]:
                value = value | perms.permissions_dict[key]

        if Role.objects.filter(name=name).exists():
            return Response("Duplicate name", status=status.HTTP_400_BAD_REQUEST)

        role = Role.objects.create(name=name, permissions=value)

        return Response(RoleSerializer(role).data)

    def partial_update(self, request, *args, **kwargs):
        # create_log(
        #     request,
        #     am_i_dealer(request),
        #     am_i_admin(request),
        #     self.request.method,
        #     "RoleViewSet-partial_update",
        # )
        value = 0
        data = request.data
        if not "name" in data:
            return Response("missing name field", status=status.HTTP_400_BAD_REQUEST)

        name = data["name"]
        del data["name"]
        for key in data:
            if not key in perms.permissions_dict:
                return Response(
                    "unknown field: " + key, status=status.HTTP_400_BAD_REQUEST
                )

            if data[key]:
                value = value | perms.permissions_dict[key]

        role = get_object_or_404(Role, pk=kwargs["pk"])
        role.name = name
        role.permissions = value
        role.save()

        return Response(RoleSerializer(role).data)

    def destroy(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "RoleViewSet-destroy",
        # )
        return super().destroy(request, *args, **kwargs)


class DealViewSet(viewsets.ModelViewSet, DealListAPIView):
    permission_classes = (SaebPermission,)
    serializer_class = DealSerializer
    saeb_sequential_permissions = perms.DEAL_VIEW
    http_method_names = ["get", "delete"]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "DealViewSet-list",
        # )
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "DealViewSet-destroy",
        # )
        return super().destroy(request, *args, **kwargs)


class DealerViewSet(viewsets.ModelViewSet):
    permission_classes = (SaebPermission,)
    queryset = Dealer.objects.all()
    serializer_class = DealerSerializer
    saeb_sequential_permissions = perms.DEALER_VIEW

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "DealerViewSet-list",
        # )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "DealerViewSet-create",
        # )
        return super().create(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.validated_data.pop("phone", None)
        serializer.save()

    def update(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "DealerViewSet-update",
        # )
        self.request.method
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        if instance.phone == instance.office.owner.phone:
            if not request.data["office"] == instance.office.id:
                return HttpResponse(
                    "Owner of an office cannot be moved to another office",
                    status=status.HTTP_400_BAD_REQUEST,
                )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "DealerViewSet-destroy",
        # )
        instance = self.get_object()
        if instance.phone == instance.office.owner.phone:
            return HttpResponse(
                "Cannot delete an office owner", status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OfficeViewSet(viewsets.ModelViewSet):
    permission_classes = (SaebPermission,)
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer
    saeb_sequential_permissions = perms.OFFICE_VIEW

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "OfficeViewSet-list",
        # )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "OfficeViewSet-create",
        # )
        # manual validation
        data = request.data
        errors = {}
        if not "name_ar" in data or not data["name_ar"]:
            errors["name_ar"] = "Missing field"
        if not "name_en" in data or not data["name_en"]:
            errors["name_en"] = "Missing field"
        if not "image" in data or not data["image"]:
            errors["image"] = "Missing field"
        if not "owner" in data or not data["owner"]:
            errors["owner"] = "Missing field"
        else:
            if not "name" in data["owner"] or not data["owner"]["name"]:
                errors["owner.name"] = "Missing field"
            if not "phone" in data["owner"] or not data["owner"]["phone"]:
                errors["owner.phone"] = "Missing field"
            elif not re.match(r"\d{8}", data["owner"]["phone"]):
                errors["owner.phone"] = "Invalid. Must be 8 numbers"

        if errors:
            return JsonResponse(errors, status=status.HTTP_400_BAD_REQUEST)

        # validate dealer field
        file_type, image_data = data["image"].split(";base64,")
        file_type = file_type[file_type.find("/") + 1 :]

        content_file = ContentFile(
            base64.b64decode(image_data), name=data["name_ar"] + "." + file_type
        )

        if Dealer.objects.filter(phone=data["owner"]["phone"]).exists():
            return Response(
                "Newly provided owner already exists as a dealer or owner in another office"
            )

        office = Office.objects.create(
            name_ar=data["name_ar"], name_en=data["name_en"], image=content_file
        )
        dealer = Dealer.objects.create(**data["owner"], office=office)
        office.owner = dealer
        office.save()

        return JsonResponse(
            OfficeSerializer(office, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    # pylint: disable=arguments-differ
    def partial_update(self, request, pk, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "OfficeViewSet-patrial_update",
        # )
        # manual validation
        data = request.data

        office = get_object_or_404(Office, pk=pk)
        if "name_ar" in data and data["name_ar"]:
            office.name_ar = data["name_ar"]
        if "name_en" in data and data["name_en"]:
            office.name_en = data["name_en"]
        if "owner" in data and data["owner"]:
            try:
                dealer = Dealer.objects.get(pk=data["owner"])
            except Dealer.DoesNotExist:
                return HttpResponse("Unkonwn owner", status=status.HTTP_404_NOT_FOUND)
            if Office.objects.filter(owner=dealer).exists():
                if not str(office.owner) == data["owner"]:
                    return HttpResponse(
                        "Newly provided owner already owns another office", status=400
                    )
            dealers_ = Dealer.objects.filter(office=office)
            dealers_in_office = []
            for n in dealers_:
                dealers_in_office.append(str(n))
            if not request.data["owner"] in dealers_in_office:
                return HttpResponse(
                    "Newly provided owner already belongs to another office"
                )
            office.owner = dealer
        if "image" in data and data["image"]:
            file_type, image_data = data["image"].split(";base64,")
            file_type = file_type[file_type.find("/") + 1 :]

            content_file = ContentFile(
                base64.b64decode(image_data), name=data["name_ar"] + "." + file_type
            )

            office.image = content_file

        office.save()

        # validate dealer field

        return JsonResponse(
            OfficeSerializer(office, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, pk, *args, **kwargs):
        # create_log(
        #     request,
        #     am_i_dealer(request),
        #     am_i_admin(request),
        #     self.request.method,
        #     "OfficeViewSet-destroy",
        # )
        if pk == "1":
            return HttpResponse("You can't do that", status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class PropertyTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (SaebPermission,)
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer
    saeb_sequential_permissions = perms.PROPERTY_VIEW

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyTypeViewSet-list",
        # )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyTypeViewSet-create",
        # )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyTypeViewSet-update",
        # )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyTypeViewSet-destroy",
        # )
        return super().destroy(request, *args, **kwargs)


class PropertyAreaViewSet(viewsets.ModelViewSet):
    permission_classes = (SaebPermission,)
    queryset = PropertyArea.objects.all()
    serializer_class = PropertyAreaSerializer
    saeb_sequential_permissions = perms.AREA_VIEW

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyAreaViewSet-list",
        # )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyAreaViewSet-create",
        # )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyAreaViewSet-update",
        # )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyAreaViewSet-destroy",
        # )
        return super().destroy(request, *args, **kwargs)


class PropertyOutlookViewSet(viewsets.ModelViewSet):
    permission_classes = (SaebPermission,)
    queryset = PropertyOutlook.objects.all()
    serializer_class = PropertyOutlookSerializer
    saeb_sequential_permissions = perms.OUTLOOK_VIEW

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyOutlookViewSet-list",
        # )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyOutlookViewSet-create",
        # )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyOutlookViewSet-update",
        # )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyOutlookViewSet-destroy",
        # )
        return super().destroy(request, *args, **kwargs)


class OfferViewSet(viewsets.ModelViewSet):
    permission_classes = (SaebPermission,)
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    saeb_sequential_permissions = perms.OFFER_VIEW

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "OfferViewSet-list",
        # )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "OfferViewSet-create",
        # )
        file_type, image_data = request.data["image"].split(";base64,")
        file_type = file_type[file_type.find("/") + 1 :]
        content_file = ContentFile(
            base64.b64decode(image_data), name=request.data["name_ar"] + "." + file_type
        )
        offer = Offer.objects.create(
            name_ar=request.data["name_ar"],
            name_en=request.data["name_en"],
            price=request.data["price"],
            credit=request.data["credit"],
            image=content_file,
        )
        return JsonResponse(
            OfferSerializer(offer, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, pk, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "OfferViewSet-partial_update",
        # )
        offer = get_object_or_404(Offer, pk=pk)
        data = request.data
        if "name_ar" in data and data["name_ar"]:
            offer.name_ar = data["name_ar"]
        if "name_en" in data and data["name_en"]:
            offer.name_en = data["name_en"]
        if "credit" in data and data["credit"]:
            offer.credit = data["credit"]
        if "price" in data and data["price"]:
            offer.price = data["price"]
        if "image" in data and data["image"]:
            file_type, image_data = data["image"].split(";base64,")
            file_type = file_type[file_type.find("/") + 1 :]
            content_file = ContentFile(
                base64.b64decode(image_data), name=data["name_ar"] + "." + file_type
            )
            offer.image = content_file
        offer.save()
        return JsonResponse(
            OfferSerializer(offer, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "OfferViewSet-destroy",
        # )
        return super().destroy(request, *args, **kwargs)


class PurchaseListAPI(generics.ListAPIView):
    http_method_names = ["get"]
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    pagination_class = DealPagination

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PurchaseListAPI-list",
        # )
        try:
            if not AdminUserSerializer(request.user.dealer.admin).data["role"][
                "PURCHASE_VIEW"
            ]:
                return HttpResponse(
                    "You do not have permission to do this",
                    status=status.HTTP_403_FORBIDDEN,
                )
            return super().list(request, *args, **kwargs)
        except:
            return HttpResponse(
                "You are not an admin", status=status.HTTP_403_FORBIDDEN
            )


class GiveAwayCreateAPI(generics.CreateAPIView):
    http_method_names = ["post"]
    serializer_class = PurchaseSerializer

    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "GiveAwayCreateAPI-create",
        # )
        try:
            if not AdminUserSerializer(request.user.dealer.admin).data["role"][
                "GIVEAWAY_CREATE"
            ]:
                return HttpResponse(
                    "You do not have permission to do this",
                    status=status.HTTP_403_FORBIDDEN,
                )
            offer_ = Offer.objects.filter(id=request.data["offer"])
            obj = get_object_or_404(offer_)
            if not offer_:
                HttpResponse("Offer does not exist!")
            request.data["credit"] = obj.credit
            request.data["indexed_date"] = get_today_indexed_date()
            return super().create(request, *args, **kwargs)
        except:
            return HttpResponse(
                "You are not an admin", status=status.HTTP_403_FORBIDDEN
            )


class TransactionListAPI(generics.ListAPIView):
    http_method_names = ["get"]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = DealPagination

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "TransactionListAPI-list",
        # )
        try:
            if not AdminUserSerializer(request.user.dealer.admin).data["role"][
                "TRANSACTION_VIEW"
            ]:
                return HttpResponse(
                    "You do not have permission to do this",
                    status=status.HTTP_403_FORBIDDEN,
                )
            return super().list(request, *args, **kwargs)
        except:
            return HttpResponse(
                "You are not an admin", status=status.HTTP_403_FORBIDDEN
            )


class DirectPayCreateAPI(generics.CreateAPIView):
    http_method_names = ["post"]
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "DirectPayCreateAPI-create",
        # )
        try:
            if not AdminUserSerializer(request.user.dealer.admin).data["role"][
                "DIRECTPAY_CREATE"
            ]:
                return HttpResponse(
                    "You do not have permission to do this",
                    status=status.HTTP_403_FORBIDDEN,
                )
            request.data["date_fullfilled"] = datetime.now()
            request.data["paymnet_id"] = randint(0, 99999)
            request.data["indexed_date"] = get_today_indexed_date()
            offer = get_object_or_404(Offer, pk=request.data["offer"])
            dealer = get_object_or_404(Dealer, phone=request.data["dealer"])
            purchase = Purchase.objects.create(
                dealer=dealer,
                credit=offer.credit,
                indexed_date=get_today_indexed_date(),
            )
            request.data["purchase"] = purchase.id
            return super().create(request, *args, **kwargs)
        except:
            return HttpResponse(
                "You are not an admin", status=status.HTTP_403_FORBIDDEN
            )


# class KWTsms_Balance_RetrieveAPIView(generics.RetrieveAPIView):
#     saeb_sequential_permissions = perms.KWTSMSBALANCE_VIEW
#     permission_classes = (SaebPermission,)


#     def retrieve(self, request, *args, **kwargs):
#         request = (
#             urlopen(
#                 "https://www.kwtsms.com/API/balance/?username="
#                 + KWTsms_username
#                 + "&password="
#                 + KWTsms_password
#             )
#             .read()
#             .decode("utf-8")
#         )
#         return Response(request)


# class KWTsms_SenderID_RetrieveAPIView(generics.RetrieveAPIView):
#     permission_classes = (SaebPermission,)
#     saeb_sequential_permissions = perms.KWTSMSSENDERID_VIEW

#     def retrieve(self, request, *args, **kwargs):
#         request = (
#             urlopen(
#                 "https://www.kwtsms.com/API/senderid/?username="
#                 + KWTsms_username
#                 + "&password="
#                 + KWTsms_password
#             )
#             .read()
#             .decode("utf-8")
#         )
#         return Response(request)

# class KWTsms_DLR_RetrieveAPIView(generics.RetrieveAPIView):
#     permission_classes = (SaebPermission,)
#     saeb_sequential_permissions = perms.KWTSMSDLR_VIEW

#     def retrieve(self, request, *args, **kwargs):
#         request = (
#             urlopen(
#                 "https://www.kwtsms.com/API/dlr/?username="
#                 + KWTsms_username
#                 + "&password="
#                 + KWTsms_password
#                 + "&msgid="
#                 + "12345678"
#             )
#             .read()
#             .decode("utf-8")
#         )
#         return Response(request)

# class KWTsms_Send_CreateAPIView(generics.CreateAPIView):
#     permission_classes = (SaebPermission,)
#     saeb_sequential_permissions = perms.KWTSMSSEND_VIEW

#     def create(self, request, *args, **kwargs):
#         phone = request.data["phone"]
#         msg = request.data["msg"].replace(" ", "+")
#         dealer = Dealer.objects.get(phone=phone)
#         if not dealer:
#             return Response("This dealer does not exist")
#         if not phone:
#             return Response("Missing phone")
#         if not msg:
#             return Response("Missing msg")
#         if ENV == "local":
#             Message.objects.create(
#                 result="OK",
#                 msg_id=create_rndm(),
#                 numbers=create_rndm(),
#                 points_charged=create_rndm(),
#                 balance_after=create_rndm(),
#                 UNIX_timestamp= datetime.today(),
#                 msg=msg,
#                 dealer=dealer,
#                 indexed_date=get_today_indexed_date(),
#             )
#             return Response({"Message": "Sent! (NOT IN PROD)"})
#         elif ENV == "prod":
#             request = (
#                 urlopen(
#                     "https://www.kwtsms.com/API/send/?username="
#                     + KWTsms_username
#                     + "&password="
#                     + KWTsms_password
#                     + "&sender=KWT-MESSAGE&mobile=965"
#                     + phone
#                     + "&lang=2&message="
#                     + msg
#                 )
#                 .read()
#                 .decode("utf-8")
#             )
#             for i in range(len(request.split(":"))):
#                 globals()["msg_info" + str(i)] = request.split(":")[i]
#             Message.objects.create(
#                 result=msg_info0,
#                 msg_id=msg_info1,
#                 numbers=msg_info2,
#                 points_charged=msg_info3,
#                 balance_after=msg_info4,
#                 UNIX_timestamp=msg_info5,
#                 msg=msg,
#                 dealer=dealer,
#                 indexed_date=get_today_indexed_date(),
#             )
#             return Response({"Message": "Sent!"})
#         # return redirect('https://www.kwtsms.com/API/send/?username='+KWTsms_username+'&password='+KWTsms_password+'&sender=KWT-MESSAGE&mobile=965'+phone+'&lang=2&message='+msg)


# class Message_ListAPIView(generics.ListAPIView):
#     serializer_class = MessageSerializer
#     queryset = Message.objects.all()
#     permission_classes = (SaebPermission,)
#     saeb_sequential_permissions = perms.MESSAGE_VIEW
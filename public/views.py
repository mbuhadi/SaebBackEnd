from django.db.models.query import QuerySet
from rest_framework import status, viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Max, Count
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from public.serializers import (
    DealSerializer,
    PropertyTypeSerializer,
    PropertyAreaSerializer,
    PropertyOutlookSerializer,
)
from public.models import Deal, PropertyType, PropertyArea, PropertyOutlook
from administration.models import DeletedDeal, DealLog
import datetime
from rest_framework import generics
from root.settings import ENV, random_string
from root.paginators import DealPagination
import os
from utility2 import visitor_ip_address, create_log, am_i_dealer, am_i_admin

User = get_user_model()


@permission_classes([AllowAny])
class DealListAPIView(generics.ListAPIView):
    serializer_class = DealSerializer
    pagination_class = DealPagination
    model = Deal

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .annotate(created=Max("logs__date"))
            .order_by("-created")
        )

    def get_queryset(self):
        # return visitor_ip_address(self.request)
        try:
            print(self.request.user.dealer)
        except:
            print("SADSANJK")
        # print(self.request.user.dealer)
        randomstring = random_string
        _deals = self.model.objects.all()
        valid_querry = [
            "property_type",
            "property_area",
            "property_outlook",
        ]
        querry = self.request.GET
        if not querry:
            return _deals
        # Creating variables(filter0, filter1 etc ..) and appending them to 'filters'
        filter_dict = {}
        for i in range(len(valid_querry)):
            filter_dict["filter%s" % i] = _deals.filter(description=randomstring)
        filters = list(filter_dict.values())
        count = 0
        for key in querry:
            if key == "page":
                continue
            if not key in valid_querry:
                return HttpResponse("Invalid query", status=400)
            vals = querry[key].split()
            for i in range(len(vals)):
                dict1 = {key: vals[i]}
                filters[count] = filters[count] | _deals.filter(**dict1)
            count = count + 1
            finalfilter = filters[0]
        for i in range(count):
            finalfilter = finalfilter & filters[i]
        return finalfilter

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "DealListAPIView-list",
        # )
        return super().list(request, *args, **kwargs)


class Testing1(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        print("O")
        # create_log(self.request, am_i_dealer(self.request), am_i_admin(self.request), "GET", "DealListAPIView-list")
        return super().list(request, *args, **kwargs)


class Testing2(Testing1):
    def list(self, request, *args, **kwargs):
        print("X")
        # create_log(self.request, am_i_dealer(self.request), am_i_admin(self.request), "GET", "DealListAPIView-list")
        return super().list(request, *args, **kwargs)


@permission_classes([AllowAny])
class PropertyTypeListAPIView(generics.ListAPIView):
    serializer_class = PropertyTypeSerializer
    queryset = PropertyType.objects.all()

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyTypeListAPIView-list",
        # )
        return super().list(request, *args, **kwargs)


@permission_classes([AllowAny])
class PropertyAreaListAPIView(generics.ListAPIView):
    serializer_class = PropertyAreaSerializer
    queryset = PropertyArea.objects.all().order_by("governorate", "name_ar")

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyAreaListAPIView-list",
        # )
        return super().list(request, *args, **kwargs)


@permission_classes([AllowAny])
class PropertyOutlookListAPIView(generics.ListAPIView):
    serializer_class = PropertyOutlookSerializer
    queryset = PropertyOutlook.objects.all()

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PropertyOutlookListAPIView-list",
        # )
        return super().list(request, *args, **kwargs)


# @permission_classes([AllowAny])
# class GetIPListAPIView(generics.ListAPIView):
#     serializer_class = PropertyAreaSerializer
#     queryset = PropertyArea.objects.all()


@permission_classes([AllowAny])
def my_get_the_IP(request):
    return HttpResponse(visitor_ip_address(request))


# API for testing code used in deal expiary feature
# @permission_classes([AllowAny])
# class TestingCreateAPIView(generics.CreateAPIView):
#     serializer_class = DealSerializer

#     def create(self, request, *args, **kwargs):
#         deals = Deal.objects.filter(created__lt=datetime.datetime.today()-datetime.timedelta(minutes=1))
#         numberofdeals = deals.count()
#         if deals:
#             for deal in deals:
#                 deal.delete()
#         return Response(numberofdeals)

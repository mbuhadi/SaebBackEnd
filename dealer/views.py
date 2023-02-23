from random import randint
from public.views import DealListAPIView
from administration.permissions import DEAL_CREATE
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from django.db.models import Max, Count
from dealer.serializers import DealerSerializer
from dealer.models import Dealer
from public.models import Deal
from administration.models import Credit, DeletedDeal
from django.shortcuts import get_object_or_404, redirect
from utility import get_today_indexed_date, get_indexed_date, create_transaction_id
from utility2 import create_log, am_i_dealer, am_i_admin
from rest_framework import generics
from administration.serializers import (
    OfferSerializer,
    TransactionSerializer,
)
from administration.models import Offer, Purchase, Transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from root.settings import (
    ENV,
    MyFatoora_Live_URL,
    MyFatoora_Live_Token,
    MyFatoora_Test_URL,
    MyFatoora_Test_Token,
)

# from root.settings import ENV
import pprint
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from utility import create_payment_id
import json
import ast
from django.utils.decorators import decorator_from_middleware, method_decorator
from root.middleware import CorsMiddleware
from rest_framework import permissions
from django.contrib.sites.shortcuts import get_current_site
from requests.models import PreparedRequest


class MyFatooraTest(permissions.BasePermission):
    def has_permission(self, request, view):
        # if str(request.META["REMOTE_ADDR"]) == "10.34.18.99":
        #     return True
        # global current_site
        current_site = get_current_site(request)
        # info = request.domain
        # print(current_site)
        return True

    def has_object_permission(self, request, view, obj):
        return True


class DealerDealViewSet(viewsets.ModelViewSet, DealListAPIView):
    def get_queryset(self):
        return super().get_queryset().filter(dealer=self.request.user.dealer)

    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "DealerDealViewSet-create",
        # )
        if request.user.dealer.remaining <= 0:
            return HttpResponse("Out of credit", status=status.HTTP_400_BAD_REQUEST)
        request.data["dealer"] = self.request.user.dealer
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "DealerDealViewSet-update",
        # )
        remanining = request.user.dealer.remaining
        if remanining <= 0:
            return HttpResponse("Out of credit", status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        instance.save()
        return JsonResponse({"remaining": remanining - 1}, status=200)


class DealerRetrieveUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = DealerSerializer
    http_method_names = ["get", "patch"]

    def get_queryset(self):
        return Dealer.objects.filter(phone=self.request.user.dealer)

    def get_object(self):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "DealerRetrieveUpdate-get_object",
        # )
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset)
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "DealerRetrieveUpdate-update",
        # )
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        request.data["phone"] = instance.phone
        request.data["office"] = instance.office.id
        return super().update(request, *args, **kwargs)


class deletedListView(DealListAPIView):
    model = DeletedDeal

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "deletedListView-list",
        # )
        return super().list(request, *args, **kwargs)


class OfferListAPI(generics.ListAPIView):
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "OfferListAPI-list",
        # )
        return super().list(request, *args, **kwargs)


class OfferCreateAPI(generics.CreateAPIView):
    serializer_class = OfferSerializer
    http_method_names = ["post"]
    throttle_scope = "transactions"

    # MyFatoora - Test url + token
    if ENV == "TEST":
        baseURL = MyFatoora_Test_URL
        token = MyFatoora_Test_Token

    # MyFatoora - Live url + token
    if ENV == "PROD":
        baseURL = MyFatoora_Live_URL
        token = MyFatoora_Live_Token

    def addSlash(self, string):
        word = "{0}".format('"') + string + "{0}".format('"')
        return word

    def create(self, request, pk, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "OfferCreateAPI",
        # )
        if not pk:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        dealer = request.user.dealer
        offer = get_object_or_404(Offer, pk=pk)
        target_dealer = None

        if "dealer" in request.query_params:
            target_dealer = request.query_params["dealer"]

        if target_dealer:
            dealer = get_object_or_404(Dealer, pk=target_dealer)

        transaction = Transaction.objects.create(
            id=create_transaction_id(),
            offer=offer,
            price=offer.price,
            dealer=dealer,
            duration=offer.duration,
            indexed_date=get_today_indexed_date(),
            redirect_destination=request.data["redirect_destination"],
        )
        if ENV == "DEV":
            payment_id = create_payment_id()
            invoice_id = create_payment_id()
            redir = "http://127.0.0.1:8000/api/dealer/fakeknet/{0}/".format(
                str(transaction.id)
            )
            newparams = {"paymentId": payment_id, "Id": invoice_id}
            req = PreparedRequest()
            req.prepare_url(redir, newparams)
            # print(req.url)
            # return HttpResponse(req.url)
            return Response(req.url)
        elif ENV == "TEST" or ENV == "PROD":
            customer_name = str(dealer.name)
            Notification_options = "LNK"  # Options are "EML", "SMS", "LNK", "ALL"
            Area_code = "+965"
            mobile = str(dealer.phone)
            InvoiceValue = str(0.2)
            display_currency = "KWD"
            callbackURL = (
                "https://saebbackend.herokuapp.com/api/dealer/payment/"
                + str(transaction.id)
                + "/"
            )
            errorURL = (
                "https://saebbackend.herokuapp.com/api/dealer/payment/"
                + str(transaction.id)
                + "/"
            )
            language = "en"
            customer_reference = str(transaction.id)
            mobile = str(dealer.phone)
            # nonEmail = "None@non.com"

            url = self.baseURL + "/v2/SendPayment"
            payload = (
                '{"CustomerName":'
                + self.addSlash(customer_name)
                + ',"NotificationOption":'
                + self.addSlash(Notification_options)
                + ',"MobileCountryCode":'
                + self.addSlash(Area_code)
                + ","
                '"CustomerMobile":'
                + self.addSlash(mobile)
                + ',"InvoiceValue":'
                + InvoiceValue
                + ","
                '"DisplayCurrencyIso":'
                + self.addSlash(display_currency)
                + ',"CallBackUrl":'
                + self.addSlash(callbackURL)
                + ',"ErrorUrl": '
                ""
                + self.addSlash(errorURL)
                + ',"Language":'
                + self.addSlash(language)
                + ',"CustomerReference": '
                + self.addSlash(customer_reference)
                + ","
                '"CustomerAddress": {"Block": '
                '"","Street": "","HouseBuildingNo": "","Address": "","AddressInstructions": ""},'
                '"InvoiceItems": [{"ItemName": "Product 01","Quantity": 1,"UnitPrice":'
                + InvoiceValue
                + "}]} "
            )
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.token,
            }
            response = requests.request("POST", url, data=payload, headers=headers)
            invoice_link = response.json()["Data"]["InvoiceURL"]
            return HttpResponse(invoice_link)
        else:
            return HttpResponse("ENV var not properly configured")


@permission_classes([AllowAny])
class FakeKNETAPIView(generics.RetrieveAPIView):
    def retrieve(self, request, pk, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "FakeKNETAPIView-retrieve",
        # )
        if not pk:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        transaction = get_object_or_404(Transaction, pk=pk)
        if transaction.date_fullfilled:
            return HttpResponse(
                "The transaction has already been fulfilled, credits have been added to your account",
                status=status.HTTP_200_OK,
            )
        transaction.payment_id = self.request.GET["paymentId"]
        transaction.date_fullfilled = datetime.now()
        purchase = Purchase.objects.create(
            dealer=transaction.dealer,
            credit=transaction.offer.credit,
            indexed_date=transaction.indexed_date,
            duration=transaction.duration,
        )
        transaction.purchase = purchase
        transaction.save()
        # Loop through number of times of duration
        credits = []
        for i in range(purchase.duration):
            date = datetime.today() + relativedelta(months=i)
            credits.append(
                Credit(
                    dealer=purchase.dealer,
                    amount=purchase.credit,
                    indexed_date=get_indexed_date(date.year, date.month),
                )
            )
        Credit.objects.bulk_create(credits)
        redir = transaction.redirect_destination
        newparams = {"transactionID": transaction.id}
        req = PreparedRequest()
        req.prepare_url(redir, newparams)
        print(req.url)
        return HttpResponse(req.url)


@permission_classes([AllowAny])
class PaymentAPI(generics.RetrieveAPIView):
    if ENV == "TEST":
        baseURL = MyFatoora_Test_URL
        token = MyFatoora_Test_Token
    if ENV == "PROD":
        baseURL = MyFatoora_Live_URL
        token = MyFatoora_Live_Token

    def addSlash(self, string):
        word = "{0}".format('"') + string + "{0}".format('"')
        return word

    def retrieve(self, request, pk, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PaymentAPI-retrieve",
        # )
        data_ = (
            '{"Key":'
            + self.addSlash(str(self.request.GET["paymentId"]))
            + ',"KeyType":"PaymentId"}'
        )
        url = self.baseURL + "/v2/GetPaymentStatus"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.token,
        }
        response = requests.request("POST", url, data=data_, headers=headers)
        invoice_status = json.loads(response.text)["Data"]["InvoiceStatus"]
        if not invoice_status == "Paid" and ENV == "PROD":
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not pk:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        transaction = get_object_or_404(Transaction, pk=pk)
        if transaction.date_fullfilled and ENV == "PROD":
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        transaction.payment_id = self.request.GET["paymentId"]
        transaction.date_fullfilled = datetime.now()
        purchase = Purchase.objects.create(
            dealer=transaction.dealer,
            credit=transaction.offer.credit,
            indexed_date=transaction.indexed_date,
            duration=transaction.duration,
        )
        transaction.purchase = purchase
        transaction.save()
        credits = []
        for i in range(purchase.duration):
            date = datetime.today() + relativedelta(months=i)
            credits.append(
                Credit(
                    dealer=purchase.dealer,
                    amount=purchase.credit,
                    indexed_date=get_indexed_date(date.year, date.month),
                )
            )
        Credit.objects.bulk_create(credits)
        redir = transaction.redirect_destination
        newparams = {"transactionID": transaction.id}
        req = PreparedRequest()
        req.prepare_url(redir, newparams)
        print(req.url)
        return HttpResponse(req.url)


@permission_classes([AllowAny])
class PaymentStatusAPI(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    # MyFatoora - Test url + token
    if ENV == "TEST":
        baseURL = MyFatoora_Test_URL
        token = MyFatoora_Test_Token

    if ENV == "PROD":
        baseURL = MyFatoora_Live_URL
        token = MyFatoora_Live_Token

    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "PaymentStatusAPI",
        # )
        url = self.baseURL + "/v2/GetPaymentStatus"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.token,
        }
        response = requests.request("POST", url, data=request.body, headers=headers)
        return HttpResponse(response.text, status=status.HTTP_200_OK)


class TranasctionAPIView(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    http_method_names = ["get"]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(dealer=self.request.user.dealer, date_fullfilled__isnull=False)
        )

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "TranasctionAPIView",
        # )
        return super().list(request, *args, **kwargs)

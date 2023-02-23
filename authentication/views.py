from administration.tasks import every_day
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models import UserAccount, TemporaryToken
from authentication.serializers import OtpSerializer, OtpCodeSerializer
from dealer.models import Dealer
from administration.models import Message
import datetime
from utility import get_today_indexed_date, create_rndm
from utility2 import create_log, am_i_dealer, am_i_admin
from rest_framework import generics
from django.shortcuts import redirect
import random
from root.settings import KWTsms_username, KWTsms_password, KWTsms_msg
from urllib.request import urlopen
import time
import requests
import os
from root.settings import ENV


@permission_classes([AllowAny])
class OTPCreateAPIView(generics.CreateAPIView):
    serializer_class = OtpSerializer
    throttle_scope = "otp"

    def generate_otp(self):
        if ENV == "DEV" or ENV == "TEST":
            return "000000"
        elif ENV == "PROD":
            return str(random.randint(100000, 999999))
        else:
            return HttpResponse("ENV var not properly configured")

    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "OTPCreateAPIView",
        # )
        try:
            dealer = Dealer.objects.get(phone=self.request.data["phone"])
        except Dealer.DoesNotExist:
            return JsonResponse(
                {"message": "phone is not registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # if len(Message.objects.filter(indexed_date=get_today_indexed_date(),dealer=dealer)) > 19:
        #     return Response({"Message":"You have request too many OTPs this month!"}, status=status.HTTP_400_BAD_REQUEST)

        if TemporaryToken.objects.filter(dealer=dealer).exists():
            TemporaryToken.objects.get(dealer=dealer).delete()

        token = TemporaryToken.objects.create(dealer=dealer, otp=self.generate_otp())
        phone = str(token.dealer)
        otp = token.otp
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if ENV == "DEV" or ENV == "TEST":
            msg = Message.objects.create(
                result="OK(LOCAL)",
                msg_id=create_rndm(),
                numbers=create_rndm(),
                points_charged=create_rndm(),
                balance_after=create_rndm(),
                UNIX_timestamp=time.time(),
                msg=KWTsms_msg,
                dealer=dealer,
                indexed_date=get_today_indexed_date(),
            )
            return Response(
                {"message": "OTP sent (LOCAL)", "time": msg.UNIX_timestamp},
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        elif ENV == "PROD":
            response = requests.get(
                "https://www.kwtsms.com/API/send/?username="
                + KWTsms_username
                + "&password="
                + KWTsms_password
                + "&sender=KWT-MESSAGE&mobile=965"
                + phone
                + "&lang=2&message="
                + KWTsms_msg
                + otp,
                verify=False,
            )
            t = str(response.text).split(":")
            Message.objects.create(
                result=t[0],
                msg_id=t[1],
                numbers=t[2],
                points_charged=t[3],
                balance_after=[4],
                UNIX_timestamp=t[5],
                msg=KWTsms_msg,
                dealer=dealer,
                indexed_date=get_today_indexed_date(),
            )
            return Response({"message": "OTP sent"})
        else:
            return HttpResponse("ENV var not properly configured")


@permission_classes([AllowAny])
class VerifyOTPAPIView(generics.CreateAPIView):
    serializer_class = OtpCodeSerializer

    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "VerifyOTPAPIView",
        # )
        try:
            dealer = Dealer.objects.get(phone=self.request.data["phone"])
            token = TemporaryToken.objects.get(dealer=dealer)
            if token.otp != self.request.data["otp"]:
                return JsonResponse({"message": "Invalid OTP"}, status=400)
            if UserAccount.objects.filter(phone=self.request.data["phone"]).exists():
                UserAccount.objects.get(phone=self.request.data["phone"]).delete()
            user = UserAccount.objects.create_user(
                phone=str(self.request.data["phone"]), dealer=dealer
            )
            user.save()
            token.delete()
            jwt = RefreshToken.for_user(user)
            body = str(jwt.access_token)

            response = JsonResponse({"access": body}, status=status.HTTP_201_CREATED)
            response.set_cookie("token", body, secure=True, httponly=True)
            return response

        except TemporaryToken.DoesNotExist:
            return JsonResponse(
                {"message": f"No OTP sent to {str(self.request.data['phone'])}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Dealer.DoesNotExist:
            return JsonResponse(
                {"message": "phone is not registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutAPIView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "LogoutAPIView",
        # )
        self.request.user.delete()
        return JsonResponse({"message": "Logout successful"}, status=status.HTTP_200_OK)

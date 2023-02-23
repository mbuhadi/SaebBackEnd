from django.urls import path
from .views import VerifyOTPAPIView, LogoutAPIView, OTPCreateAPIView

urlpatterns = [
    path('logout/', LogoutAPIView.as_view()),
    path('otp/', OTPCreateAPIView.as_view()),
    path('verify/', VerifyOTPAPIView.as_view()),
]
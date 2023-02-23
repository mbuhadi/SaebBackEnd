from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from public import views

urlpatterns = [
    path("", views.DealListAPIView.as_view(), name="deals"),
    path("types", views.PropertyTypeListAPIView.as_view(), name="propertytypes"),
    path("areas", views.PropertyAreaListAPIView.as_view(), name="propertyarea"),
    path(
        "outlooks", views.PropertyOutlookListAPIView.as_view(), name="propertyoutlook"
    ),
    url(r"^getmyip/$", views.my_get_the_IP, name="IP")
    # path("test", views.TestingCreateAPIView.as_view(), name="testingAPI")
]

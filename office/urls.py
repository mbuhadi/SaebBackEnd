from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from office import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()

router.register("dealer", views.OfficeDealerViewset, 'dealer')

urlpatterns = [
    path("", views.OfficeDetailsListView.as_view()),
    path("deals", views.OfficeDealsListView.as_view()),
    path("swapowner", views.DealerOwnerUpdateAPIView.as_view())
] + router.urls

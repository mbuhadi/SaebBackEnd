from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from dealer import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
# router.trailing_slash = "/?"
router.register("deals", views.DealerDealViewSet, 'deals')
router.register("transactions", views.TranasctionAPIView, 'transactions')

urlpatterns = [
    path("deleted", views.deletedListView.as_view()),
    path("", views.DealerRetrieveUpdate.as_view()),
    path("fakeknet/<pk>/", views.FakeKNETAPIView.as_view()),
    path("offers", views.OfferListAPI.as_view()),
    path("offers/<pk>", views.OfferCreateAPI.as_view()),
    path("payment/<int:pk>/", views.PaymentAPI.as_view()),
    path("paymentstatus/", views.PaymentStatusAPI.as_view()),
] + router.urls
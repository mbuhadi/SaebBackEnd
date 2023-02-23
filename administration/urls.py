from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from administration import views
from rest_framework.routers import SimpleRouter
import absoluteuri
from root.settings import KWTsms_username, KWTsms_password, KWTsms_msg

router = SimpleRouter()
router.trailing_slash = "/?"
router.register("roles", views.RoleViewSet, 'roles')
router.register("deals", views.DealViewSet, "deals")
router.register("dealers", views.DealerViewSet, "dealers")
router.register("offices", views.OfficeViewSet, "offices")
router.register("propertytype", views.PropertyTypeViewSet, "PropertyType")
router.register("propertyarea", views.PropertyAreaViewSet, "PropertyArea")
router.register("propertyoutlook", views.PropertyOutlookViewSet, "PropertyOutlook")
router.register("offer", views.OfferViewSet, "offer")
# router.register("purchase", views.PurchaseViewSet, "purchase")
# router.register("transaction", views.TransactionViewSet, "transaction")

urlpatterns = [
    path("permissions", views.get_permissions, name="get_permissions"),
    path("purchases", views.PurchaseListAPI.as_view(), name="purchases"),
    path("giveaway", views.GiveAwayCreateAPI.as_view(), name="giveaway"),
    path("transactions", views.TransactionListAPI.as_view(), name="transactions"),
    path("directpay", views.DirectPayCreateAPI.as_view(), name="directpay"),
    # path("kwtsms/balance", views.KWTsms_Balance_RetrieveAPIView.as_view(), name="balance"),
    # path("kwtsms/senderid", views.KWTsms_SenderID_RetrieveAPIView.as_view(), name="senderid"),
    # path("kwtsms/send", views.KWTsms_Send_CreateAPIView.as_view(), name="senderid"),
    # path("kwtsms/dlr", views.KWTsms_DLR_RetrieveAPIView.as_view())
] + router.urls
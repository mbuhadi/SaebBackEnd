from django.contrib import admin
from django.urls import path, include
import root.settings as settings
from django.conf.urls.static import static

# import dealer.views as views

COMMON_PATH = "api/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(COMMON_PATH + "deals/", include("public.urls")),
    path(COMMON_PATH + "office/", include("office.urls")),
    path(COMMON_PATH + "auth/", include("authentication.urls")),
    path(COMMON_PATH + "admin/", include("administration.urls")),
    path(COMMON_PATH + "dealer/", include("dealer.urls")),
    # path(COMMON_PATH + "profile", views.profile),
]

try:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
except:
    pass

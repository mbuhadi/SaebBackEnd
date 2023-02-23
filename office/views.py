from django.db.models.query import QuerySet
from office.models import Office
from dealer.models import Dealer
from public.models import Deal
from django.db.models import Max
from office.serializers import OfficeSerializer, OfficeSummerySerializer
from public.serializers import DealSerializer
from dealer.serializers import DealerSummerySerializer
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from root.paginators import StandardResultsSetPagination
from rest_framework import status, viewsets
from rest_framework import generics
from rest_framework.response import Response
from utility2 import create_log, am_i_dealer, am_i_admin


class OfficeDetailsListView(generics.ListAPIView):
    serializer_class = OfficeSerializer

    def get_queryset(self):
        queryset = Office.objects.filter(owner=self.request.user.dealer.phone)
        return queryset

    def list(self, request, *args, **kwargs):
        # create_log(self.request, am_i_dealer(self.request), am_i_admin(self.request), "GET", "OfficeDetailsListView")
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            return HttpResponse("FORBIDDEN", status=status.HTTP_403_FORBIDDEN)

        return JsonResponse(
            OfficeSerializer(queryset[0], context={"request": request}).data, safe=False
        )


# The logic in OfficeDealsListView a dealer can only be the owner of one office
class OfficeDealsListView(generics.ListAPIView):
    serializer_class = DealSerializer
    paginate_by = 20

    def get_queryset(self):
        office = self.request.user.dealer.office
        queryset = (
            Deal.objects.filter(dealer__office=office)
            .annotate(created=Max("logs__date"))
            .order_by("-created")
        )
        return queryset

    def list(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "OfficeDealsListView",
        # )
        office = self.request.user.dealer.office
        me = self.request.user.dealer
        if not me == office.owner:
            return HttpResponse("FORBIDDEN", status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)


class OfficeDealerViewset(viewsets.ModelViewSet):
    serializer_class = DealerSummerySerializer
    http_method_names = ["post", "delete"]

    def get_queryset(self):
        queryset = Dealer.objects.filter(office=self.request.user.dealer.office)
        return queryset

    def create(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "OfficeDealerViewset-create",
        # )
        office = self.request.user.dealer.office
        me = self.request.user.dealer
        if not me == office.owner:
            return HttpResponse(
                "FORBIDDEN",
                status=status.HTTP_403_FORBIDDEN,
            )
        request.data["office"] = self.request.user.dealer.office.id
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # create_log(
        #     self.request,
        #     am_i_dealer(self.request),
        #     am_i_admin(self.request),
        #     self.request.method,
        #     "OfficeDealsListView-destroy",
        # )
        office = self.request.user.dealer.office
        me = self.request.user.dealer
        if not me == office.owner:
            return HttpResponse(
                "FORBIDDEN",
                status=status.HTTP_403_FORBIDDEN,
            )
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DealerOwnerUpdateAPIView(generics.UpdateAPIView):
    serializer_class = OfficeSummerySerializer

    def get_queryset(self):
        queryset = Office.objects.filter(owner=self.request.user.dealer)
        return queryset

    def get_object(self):
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
        #     "DealerOwnerUpdateAPIView",
        # )
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        if not instance:
            return HttpResponse("YOU ARE NOT THE OWNER!")
        request.data["name_ar"] = instance.name_ar
        request.data["name_en"] = instance.name_en
        request.data["image"] = instance.image
        dealers_ = Dealer.objects.filter(office=request.user.dealer.office)
        dealers_in_office = []
        for n in dealers_:
            dealers_in_office.append(str(n))
        if not request.data["owner"] in dealers_in_office:
            return HttpResponse("This dealer does not belong to this office")
        return super().update(request, *args, **kwargs)

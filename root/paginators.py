from rest_framework import pagination
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 20
    page_query_param = 'page'
    page_size_query_param = 'per_page'
    max_page_size = 200

class DealPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"

from datetime import datetime
import random

def get_last_month_indexed_date() -> int:
    """
    Returns indexed date of today. Etc: year: 2020, month: 5 => 202005
    """
    today = datetime.today()
    return get_indexed_date(today.year, today.month - 1)


def get_today_indexed_date() -> int:
    """
    Returns indexed date of today. Etc: year: 2020, month: 5 => 202005
    """
    today = datetime.today()
    return get_indexed_date(today.year, today.month)


def get_indexed_date(year: int, month: int) -> int:
    """
    Returns indexed date. Etc: year: 2020, month: 5 => 202005
    ### Supports negative months
    """
    # month_ = month % 12
    if month <= 0:
        month += 12
    return year * 100 + month

def create_rndm():
    return str(random.randint(10000, 99999))

def create_reference_id():
    return str(random.randint(1000000000, 9999999999))

def create_transaction_id():
    return str(random.randint(100000000, 999999999))

def create_payment_id():
    return str(random.randint(100000000000000000, 999999999999999999))

def create_invoice_id():
    return str(random.randint(100000000000000000, 999999999999999999))





# def get_client_ip(request):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         print("returning FORWARDED_FOR")
#         ip = x_forwarded_for.split(',')[-1].strip()
#     elif request.META.get('HTTP_X_REAL_IP'):
#         print("returning REAL_IP")
#         ip = request.META.get('HTTP_X_REAL_IP')
#     else:
#         print("returning REMOTE_ADDR")
#         ip = request.META.get('REMOTE_ADDR')
#     return ip
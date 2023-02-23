from administration.models import Log

def visitor_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def create_log(request,isdealer,isadmin,req_type,req_route):
    ip_= visitor_ip_address(request)
    Log.objects.create(ip_address=ip_,is_dealer=isdealer,is_admin=isadmin,type_of_request=req_type,route_of_request= req_route)

def am_i_dealer(request):
        try:
            request.user.dealer
            return True
        except:
            return False

def am_i_admin(request):
        try:
            request.user.dealer.admin
            return True
        except:
            return False
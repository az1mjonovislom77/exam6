from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponse
from datetime import time

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the request details
        print(f"Request Method: {request.method}, Request Path: {request.path}")
        response = self.get_response(request)
        return response


class AutoLogoutMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity is not None:
                difference_time = (now() - now().fromisoformat(last_activity)).total_seconds()
                if difference_time > settings.SESSION_COOKIE_AGE:
                    logout(request)
                    return redirect('shop:product')

            request.session['last_activity'] = now().isoformat()

        response = self.get_response(request)
        return response


class TimeRestrictedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_time = now().time()
        if time(1, 0) < current_time < time(2, 0): 
            return HttpResponse("Sayt shu vaqt oralig‘ida yopiq.", status=403)
        return self.get_response(request)


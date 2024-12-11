from django.http import HttpResponseForbidden

class RestrictIPMiddleware:
    ALLOWED_IPS = ['192.168.100.96,localhost,127.0.0.1']  # Replace with your Wi-Fi IP address

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        if ip not in self.ALLOWED_IPS:
            return HttpResponseForbidden("You are not allowed to access this site.")
        return self.get_response(request)

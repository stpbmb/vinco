from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if isinstance(request.user, AnonymousUser):
            return self.get_response(request)

        if not hasattr(request, 'organization'):
            # Skip organization check for admin URLs
            if request.path.startswith('/admin/'):
                return self.get_response(request)

            # Skip organization check for organization selection
            if request.path.startswith('/organizations/'):
                return self.get_response(request)

            # Redirect to organization selection
            return redirect('organizations:select')

        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip middleware for admin views
        if request.path.startswith('/admin/'):
            return None

        # Skip middleware for organization selection views
        if request.path.startswith('/organizations/'):
            return None

        if not request.user.is_authenticated:
            return None

        if not hasattr(request, 'organization'):
            return redirect('organizations:select')

        return None

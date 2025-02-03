from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from .models import OrganizationUser

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip tenant handling for excluded paths
        excluded_paths = ['/admin/', '/accounts/', '/organizations/select/']
        if any(request.path.startswith(path) for path in excluded_paths):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        # Get user's organizations
        org_user = OrganizationUser.objects.filter(
            user=request.user,
            organization__is_active=True
        ).first()

        if not org_user:
            return redirect('organizations:select')

        # Set organization context
        request.organization = org_user.organization
        request.organization_user = org_user
        
        response = self.get_response(request)
        return response

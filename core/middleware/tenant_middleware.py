from django.shortcuts import redirect
from django.urls import reverse, resolve, Resolver404
from django.contrib.auth.models import AnonymousUser
from organizations.models import Organization
import logging

logger = logging.getLogger(__name__)

class TenantMiddleware:
    """
    Middleware to ensure users have selected an organization before accessing protected views.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Skip middleware for anonymous users
            if isinstance(request.user, AnonymousUser):
                return self.get_response(request)

            # Skip middleware for static and media files
            if request.path.startswith(('/static/', '/media/')):
                return self.get_response(request)

            # Skip middleware for admin URLs
            if request.path.startswith('/admin/'):
                return self.get_response(request)

            # Skip middleware for auth URLs
            if request.path.startswith(('/login/', '/logout/', '/password_change/')):
                return self.get_response(request)

            # Skip middleware for favicon and other browser requests
            if request.path in ['/favicon.ico']:
                return self.get_response(request)

            # Check if this is the organization selection page
            try:
                current_url = resolve(request.path_info)
                if current_url.namespace == 'organizations' and current_url.url_name == 'select':
                    return self.get_response(request)
            except Resolver404:
                # If URL doesn't resolve, let Django handle it
                return self.get_response(request)

            # Check if user is authenticated
            if not request.user.is_authenticated:
                return self.get_response(request)

            # Get organization from session
            org_id = request.session.get('organization_id')
            logger.info(f"Organization ID from session: {org_id}")

            if org_id:
                try:
                    # Verify organization exists and user has access
                    organization = Organization.objects.get(
                        id=org_id,
                        organizationuser__user=request.user,
                        is_active=True
                    )
                    logger.info(f"Found organization: {organization.name}")
                    request.organization = organization
                    return self.get_response(request)
                except Organization.DoesNotExist:
                    logger.warning(f"Organization {org_id} not found or user has no access")
                    if 'organization_id' in request.session:
                        del request.session['organization_id']
                        request.session.save()

            # Store the current URL to redirect back after organization selection
            # Only store if it's not the root URL or organization select
            if request.path not in ['/', '/organizations/select/']:
                request.session['next'] = request.get_full_path()
                request.session.save()
                logger.info(f"Stored next URL in session: {request.get_full_path()}")

            return redirect('organizations:select')

        except Exception as e:
            logger.error(f"Error in TenantMiddleware: {str(e)}")
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

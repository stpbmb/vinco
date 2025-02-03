from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

class TenantViewMixin(LoginRequiredMixin):
    """
    Mixin to ensure views are accessed within the context of an organization.
    All organization context and redirect logic is handled by TenantMiddleware.
    This mixin only ensures the view requires login and provides organization context.
    """
    def dispatch(self, request, *args, **kwargs):
        # First check if user is authenticated (handled by LoginRequiredMixin)
        response = super().dispatch(request, *args, **kwargs)
        if response.status_code == 302:  # If redirecting to login
            return response
            
        # Organization context is handled by TenantMiddleware
        # This just provides a safety check
        if not hasattr(request, 'organization'):
            logger.warning("No organization in request - this should be handled by TenantMiddleware")
            return redirect('organizations:select')
            
        return response

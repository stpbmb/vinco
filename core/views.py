from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

# Create your views here.

class TenantViewMixin(LoginRequiredMixin):
    """
    Mixin to handle organization-based filtering in views.
    """
    def get_queryset(self):
        """Filter queryset by the user's organization."""
        queryset = super().get_queryset()
        return queryset.filter(organization=self.request.organization)

    def form_valid(self, form):
        """Set the organization before saving the form."""
        form.instance.organization = self.request.organization
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        """Check if user has access to the organization."""
        if not hasattr(request, 'organization'):
            return redirect('organizations:select')
        return super().dispatch(request, *args, **kwargs)

def handler404(request, exception):
    """Handle 404 Not Found errors."""
    context = {'title': 'Page Not Found'}
    return render(request, 'core/404.html', context, status=404)

def handler500(request):
    """Handle 500 Server Error."""
    context = {'title': 'Server Error'}
    return render(request, 'core/500.html', context, status=500)

def handler403(request, exception):
    """Handle 403 Forbidden errors."""
    context = {'title': 'Access Denied'}
    return render(request, 'core/403.html', context, status=403)

def handler400(request, exception):
    """Handle 400 Bad Request errors."""
    context = {'title': 'Bad Request'}
    return render(request, 'core/400.html', context, status=400)

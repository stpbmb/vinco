from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from core.views.mixins import TenantViewMixin
from vineyards.models import Vineyard
from harvests.models import Harvest
from cellars.models import Cellar
from packaging.models import Bottle, Label, Closure, Box
import logging

logger = logging.getLogger(__name__)

class DashboardView(TenantViewMixin, TemplateView):
    """
    Main dashboard view that shows overview of the winery operations.
    """
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Get organization from request (set by TenantViewMixin)
            organization = self.request.organization
            logger.info(f"Getting dashboard data for organization: {organization.name}")
            
            # Get counts for each model
            context['vineyard_count'] = Vineyard.objects.filter(organization=organization).count()
            context['active_harvests'] = Harvest.objects.filter(organization=organization, is_active=True).count()
            context['cellar_count'] = Cellar.objects.filter(organization=organization).count()
            
            # Get packaging counts
            context['bottle_count'] = Bottle.objects.filter(organization=organization).count()
            context['label_count'] = Label.objects.filter(organization=organization).count()
            context['closure_count'] = Closure.objects.filter(organization=organization).count()
            context['box_count'] = Box.objects.filter(organization=organization).count()
            
            logger.info(f"Dashboard data: {context}")
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            context['error'] = 'An error occurred while loading the dashboard.'
            
        context['title'] = 'Dashboard'
        return context

dashboard = DashboardView.as_view()

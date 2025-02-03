from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from .models import Organization
import logging

logger = logging.getLogger(__name__)

@login_required
def organization_select(request):
    """
    View for selecting an organization to work with.
    """
    try:
        # Log request details
        logger.info(f"Organization select view - Path: {request.path_info}, User: {request.user}, Method: {request.method}")
        logger.info(f"Session data: {dict(request.session)}")
        
        # Get available organizations
        organizations = Organization.objects.filter(
            organizationuser__user=request.user,
            is_active=True
        ).distinct()
        
        logger.info(f"Found organizations: {list(organizations.values('id', 'name'))}")
        
        if not organizations.exists():
            logger.warning(f"User {request.user.username} has no organizations")
            return render(request, 'organizations/select.html', {
                'organizations': [],
                'error': 'You do not have access to any organizations.'
            })
            
        # Handle organization selection
        if request.method == 'POST':
            org_id = request.POST.get('organization')
            logger.info(f"Organization ID from POST: {org_id}")
            
            if org_id:
                try:
                    with transaction.atomic():
                        # Verify organization exists and user has access
                        organization = organizations.get(id=org_id)
                        
                        # Save organization ID to session and force save
                        request.session['organization_id'] = str(org_id)
                        request.session.save()
                        logger.info(f"Organization {organization.name} selected and session saved")
                        
                        # Verify the session was saved
                        saved_org_id = request.session.get('organization_id')
                        if saved_org_id != str(org_id):
                            logger.error("Session save failed - organization ID mismatch")
                            raise Exception("Session save failed")
                        
                        # Get the next URL from session or default to dashboard
                        next_url = request.session.pop('next', None)
                        request.session.save()
                        logger.info(f"Next URL from session: {next_url}")
                        
                        if next_url and next_url not in ['/', '/organizations/select/']:
                            logger.info(f"Redirecting to next URL: {next_url}")
                            return redirect(next_url)
                            
                        logger.info("Redirecting to dashboard")
                        return redirect('core:dashboard')
                except Organization.DoesNotExist:
                    logger.warning(f"Organization {org_id} not found or user has no access")
                except Exception as e:
                    logger.error(f"Error saving organization selection: {str(e)}")
                    return render(request, 'organizations/select.html', {
                        'organizations': organizations,
                        'error': 'Failed to save organization selection. Please try again.'
                    })
            else:
                logger.warning("No organization ID received in POST request")
        
        # Show organization selection form
        # For GET requests, always show the form to prevent redirect loops
        logger.info("Rendering organization selection form")
        return render(request, 'organizations/select.html', {
            'organizations': organizations,
        })
            
    except Exception as e:
        logger.error(f"Error in organization_select view: {str(e)}")
        raise

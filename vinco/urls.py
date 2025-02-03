"""vinco URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth import views as auth_views

# Error handlers must be strings
handler404 = 'core.views.error_handlers.handler404'
handler500 = 'core.views.error_handlers.handler500'
handler403 = 'core.views.error_handlers.handler403'
handler400 = 'core.views.error_handlers.handler400'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/organizations/select/', permanent=False)),
    
    # Favicon
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    
    # App URLs - include app namespaces
    path('core/', include(('core.urls', 'core'), namespace='core')),
    path('organizations/', include(('organizations.urls', 'organizations'), namespace='organizations')),
    path('vineyards/', include(('vineyards.urls', 'vineyards'), namespace='vineyards')),
    path('harvests/', include(('harvests.urls', 'harvests'), namespace='harvests')),
    path('cellars/', include(('cellars.urls', 'cellars'), namespace='cellars')),
    path('packaging/', include(('packaging.urls', 'packaging'), namespace='packaging')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

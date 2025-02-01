"""
Custom middleware for request logging and performance monitoring.
"""

import time
import logging
import uuid
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('vinco')

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests and their processing time.
    """
    
    def process_request(self, request):
        """Store the start time of the request."""
        request.start_time = time.time()
        request.request_id = str(uuid.uuid4())
        
        # Log the incoming request
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'request_id': request.request_id,
                'method': request.method,
                'path': request.path,
                'user': request.user.username if request.user.is_authenticated else 'anonymous',
                'ip': request.META.get('REMOTE_ADDR'),
            }
        )

    def process_response(self, request, response):
        """Log the completion of the request."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log the response
            logger.info(
                f"Request finished: {request.method} {request.path}",
                extra={
                    'request_id': getattr(request, 'request_id', 'unknown'),
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration': duration,
                    'user': request.user.username if request.user.is_authenticated else 'anonymous',
                }
            )
            
            # Add the request ID to the response headers
            response['X-Request-ID'] = getattr(request, 'request_id', 'unknown')
        
        return response

class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers and perform basic security checks.
    """
    
    def process_response(self, request, response):
        """Add security headers to the response."""
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add Content Security Policy header
        csp_policies = [
            "default-src 'self'",
            "img-src 'self' data: https:",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
            "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
            "connect-src 'self'",
        ]
        response['Content-Security-Policy'] = '; '.join(csp_policies)
        
        return response

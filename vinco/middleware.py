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

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.RATELIMIT_ENABLE:
            return self.get_response(request)

        ip = self.get_client_ip(request)
        path = request.path

        # Special rate limit for login attempts
        if path == settings.LOGIN_URL:
            if not self.check_login_rate_limit(ip):
                logger.warning(f"Rate limit exceeded for login attempts from IP: {ip}")
                messages.error(request, "Too many login attempts. Please try again later.")
                return HttpResponseTooManyRequests("Too many login attempts")

        # General rate limit for other views
        if not self.check_view_rate_limit(ip, path):
            logger.warning(f"Rate limit exceeded for path {path} from IP: {ip}")
            messages.error(request, "Too many requests. Please try again later.")
            return HttpResponseTooManyRequests("Too many requests")

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def check_login_rate_limit(self, ip):
        key = f"login_ratelimit_{ip}"
        limit = self.parse_limit(settings.RATELIMIT_LOGIN_LIMIT)
        return self.check_limit(key, limit)

    def check_view_rate_limit(self, ip, path):
        key = f"view_ratelimit_{ip}_{path}"
        limit = self.parse_limit(settings.RATELIMIT_VIEW_LIMIT)
        return self.check_limit(key, limit)

    def parse_limit(self, limit_str):
        count, period = limit_str.split('/')
        count = int(count)
        if period.endswith('m'):
            period_seconds = int(period[:-1]) * 60
        elif period.endswith('h'):
            period_seconds = int(period[:-1]) * 3600
        else:
            period_seconds = int(period)
        return count, period_seconds

    def check_limit(self, key, limit):
        count, period = limit
        now = int(time.time())
        
        # Get the current window data
        window_data = cache.get(key, {'count': 0, 'window_start': now})
        
        # If the window has expired, reset the counter
        if now - window_data['window_start'] >= period:
            window_data = {'count': 0, 'window_start': now}
        
        # Increment the counter
        window_data['count'] += 1
        
        # Update the cache
        cache.set(key, window_data, period)
        
        # Check if limit is exceeded
        return window_data['count'] <= count

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

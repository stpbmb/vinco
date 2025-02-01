"""
Rate limiting middleware for request throttling.

This module provides middleware for implementing rate limiting on views and
login attempts to prevent abuse.
"""

import time
import logging
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from typing import Optional, Tuple, Any

logger = logging.getLogger('vinco')

class HttpResponseTooManyRequests(HttpResponse):
    """Response returned when rate limit is exceeded."""
    status_code = 429

class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to implement rate limiting for views and login attempts.
    
    This middleware checks rate limits before processing requests and can
    block requests that exceed configured limits.
    """
    
    def process_request(self, request) -> Optional[HttpResponse]:
        """
        Check rate limits before processing the request.
        
        Args:
            request: The HTTP request
            
        Returns:
            HttpResponse if rate limit exceeded, None otherwise
        """
        if not getattr(settings, 'RATELIMIT_ENABLE', False):
            return None
            
        ip = self.get_client_ip(request)
        path = request.path
        
        # Check login rate limit
        if path == '/login/':
            if not self.check_login_rate_limit(ip):
                logger.warning(f"Login rate limit exceeded for IP: {ip}")
                messages.error(request, "Too many login attempts. Please try again later.")
                return HttpResponseTooManyRequests("Too many login attempts")
                
        # Check view rate limit
        if not self.check_view_rate_limit(ip, path):
            logger.warning(f"View rate limit exceeded for IP: {ip}, path: {path}")
            messages.error(request, "Too many requests. Please try again later.")
            return HttpResponseTooManyRequests("Too many requests")
            
        return None
        
    def get_client_ip(self, request) -> str:
        """
        Get the client's IP address from the request.
        
        Args:
            request: The HTTP request
            
        Returns:
            Client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
        
    def check_login_rate_limit(self, ip: str) -> bool:
        """
        Check if login attempts are within rate limit.
        
        Args:
            ip: Client IP address
            
        Returns:
            True if within limit, False if exceeded
        """
        limit = getattr(settings, 'RATELIMIT_LOGIN_LIMIT', '5/h')
        return self.check_limit(f'login_rate_{ip}', limit)
        
    def check_view_rate_limit(self, ip: str, path: str) -> bool:
        """
        Check if view requests are within rate limit.
        
        Args:
            ip: Client IP address
            path: Request path
            
        Returns:
            True if within limit, False if exceeded
        """
        limit = getattr(settings, 'RATELIMIT_VIEW_LIMIT', '100/h')
        return self.check_limit(f'view_rate_{ip}_{path}', limit)
        
    def parse_limit(self, limit_str: str) -> Tuple[int, int]:
        """
        Parse rate limit string in format 'number/period'.
        
        Args:
            limit_str: String in format 'number/period' where period is in s, m, or h
            
        Returns:
            Tuple of (number, period_in_seconds)
        """
        number, period = limit_str.split('/')
        number = int(number)
        
        if period.endswith('s'):
            seconds = int(period[:-1])
        elif period.endswith('m'):
            seconds = int(period[:-1]) * 60
        elif period.endswith('h'):
            seconds = int(period[:-1]) * 3600
        else:
            seconds = int(period)
            
        return number, seconds
        
    def check_limit(self, key: str, limit: str) -> bool:
        """
        Check if the number of requests is within the rate limit.
        
        Args:
            key: Cache key for tracking requests
            limit: Rate limit string
            
        Returns:
            True if within limit, False if exceeded
        """
        try:
            number, seconds = self.parse_limit(limit)
        except (ValueError, TypeError):
            logger.error(f"Invalid rate limit format: {limit}")
            return True
            
        now = time.time()
        timestamps = cache.get(key, [])
        timestamps = [ts for ts in timestamps if ts > now - seconds]
        
        if len(timestamps) >= number:
            return False
            
        timestamps.append(now)
        cache.set(key, timestamps, timeout=seconds)
        return True

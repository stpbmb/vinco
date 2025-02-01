"""
Custom exceptions and exception handling utilities for the Vinco application.
"""

import logging
import uuid
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render

logger = logging.getLogger('vinco')

class VincoError(Exception):
    """Base exception class for Vinco application."""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code

class InvalidOperationError(VincoError):
    """Raised when an operation is invalid in the current context."""
    pass

class ResourceNotFoundError(VincoError):
    """Raised when a requested resource is not found."""
    pass

class ValidationError(VincoError):
    """Raised when data validation fails."""
    pass

def handle_view_exception(view_func):
    """
    Decorator to handle exceptions in views.
    
    This decorator catches common exceptions and renders appropriate error pages,
    while also logging the errors for monitoring.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Http404 as e:
            logger.warning(f"404 error: {str(e)}", extra={
                'request_path': request.path,
                'user': request.user.username
            })
            return render(request, 'errors/404.html', {
                'error_code': '404',
                'request_path': request.path
            }, status=404)
        except PermissionDenied as e:
            logger.warning(f"403 error: {str(e)}", extra={
                'request_path': request.path,
                'user': request.user.username
            })
            return render(request, 'errors/403.html', {
                'error_code': '403',
                'request_path': request.path
            }, status=403)
        except VincoError as e:
            request_id = str(uuid.uuid4())
            logger.error(f"Application error: {str(e)}", extra={
                'request_id': request_id,
                'error_code': e.code,
                'request_path': request.path,
                'user': request.user.username
            })
            return render(request, 'errors/500.html', {
                'error_code': e.code or '500',
                'request_id': request_id
            }, status=500)
        except Exception as e:
            request_id = str(uuid.uuid4())
            logger.exception(f"Unhandled error: {str(e)}", extra={
                'request_id': request_id,
                'request_path': request.path,
                'user': request.user.username
            })
            return render(request, 'errors/500.html', {
                'error_code': '500',
                'request_id': request_id
            }, status=500)
    return wrapper

def log_error(error, request=None, extra=None):
    """
    Utility function to log errors with consistent formatting.
    
    Args:
        error: The error object or message
        request: Optional Django request object
        extra: Optional dict of extra information to log
    """
    extra_data = {
        'request_id': str(uuid.uuid4()),
    }
    
    if request:
        extra_data.update({
            'request_path': request.path,
            'user': request.user.username if request.user.is_authenticated else 'anonymous',
            'method': request.method,
        })
    
    if extra:
        extra_data.update(extra)
    
    if isinstance(error, Exception):
        logger.exception(str(error), extra=extra_data)
    else:
        logger.error(str(error), extra=extra_data)

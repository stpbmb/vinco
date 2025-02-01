"""
Core exceptions and error handling utilities.

This module provides custom exceptions and utilities for consistent error handling
across the application.
"""

import logging
import uuid
from typing import Optional, Any, Dict

logger = logging.getLogger('vinco')

class VincoError(Exception):
    """Base exception for all application-specific errors."""
    def __init__(self, message: str, code: Optional[str] = None, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

class ValidationError(VincoError):
    """Raised when data validation fails."""
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message, code, status_code=400)

class ResourceNotFoundError(VincoError):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message, code, status_code=404)

class InvalidOperationError(VincoError):
    """Raised when an operation cannot be performed."""
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message, code, status_code=400)

def log_error(logger: logging.Logger, error: Exception, **kwargs: Any) -> None:
    """
    Log an error with additional context information.
    
    Args:
        logger: The logger instance to use
        error: The exception to log
        **kwargs: Additional context to include in the log
    """
    extra = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        **kwargs
    }
    
    if isinstance(logger, logging.Logger):
        logger.error(f"{type(error).__name__}: {str(error)}", extra=extra)
    else:
        # Handle Http404 and other non-logger objects
        logging.getLogger('vinco').error(f"{type(error).__name__}: {str(error)}", extra=extra)

def handle_view_exception(view_func):
    """
    Decorator to handle view exceptions consistently.
    
    Args:
        view_func: The view function to wrap
        
    Returns:
        Wrapped function that handles exceptions
    """
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except VincoError as e:
            request_id = str(uuid.uuid4())
            log_error(logger, e, 
                     request_id=request_id,
                     request_path=request.path,
                     user=request.user.username)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'error': str(e),
                    'code': e.code,
                    'request_id': request_id
                }, status=e.status_code)
                
            from django.contrib import messages
            from django.shortcuts import redirect
            messages.error(request, str(e))
            return redirect('home')
            
    return wrapper

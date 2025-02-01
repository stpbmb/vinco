"""
Shared test fixtures for all apps.
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

@pytest.fixture
def test_password():
    """Return a test password."""
    return 'testpass123'

@pytest.fixture
def create_user(db, django_user_model, test_password):
    """Create a user with the given username."""
    def make_user(username='testuser', email='test@example.com', **kwargs):
        kwargs['password'] = test_password
        if 'email' not in kwargs:
            kwargs['email'] = email
        return django_user_model.objects.create_user(username, **kwargs)
    return make_user

@pytest.fixture
def auto_login_user(db, client, create_user, test_password):
    """Create and login a user."""
    def make_auto_login(user=None):
        if user is None:
            user = create_user()
        client.login(username=user.username, password=test_password)
        return client, user
    return make_auto_login

@pytest.fixture
def add_model_permissions():
    """Add all permissions for a model to a user."""
    def add_permissions(user, model_class):
        content_type = ContentType.objects.get_for_model(model_class)
        permissions = Permission.objects.filter(content_type=content_type)
        user.user_permissions.add(*permissions)
        return permissions
    return add_permissions

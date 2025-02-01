"""
Integration tests for vineyard views.
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from vineyards.models import Vineyard, Supplier

User = get_user_model()

@pytest.fixture
def authenticated_client(client):
    """Create an authenticated client with required permissions."""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    # Add required permissions
    content_type = ContentType.objects.get_for_model(Vineyard)
    permissions = Permission.objects.filter(content_type=content_type)
    user.user_permissions.add(*permissions)
    
    content_type = ContentType.objects.get_for_model(Supplier)
    permissions = Permission.objects.filter(content_type=content_type)
    user.user_permissions.add(*permissions)
    
    client.login(username='testuser', password='testpass123')
    return client, user

@pytest.fixture
def vineyard_data():
    """Return valid vineyard form data."""
    return {
        'name': 'Test Vineyard',
        'location': 'Test Location',
        'grape_variety': 'merlot',
        'size': 1.0,
        'ownership_type': 'owned',
    }

@pytest.fixture
def supplier_data():
    """Return valid supplier form data."""
    return {
        'name': 'Test Supplier',
        'address': 'Test Address',
        'oib': '12345678901',
    }

@pytest.mark.django_db
class TestVineyardViews:
    """Test cases for vineyard views."""

    def test_vineyard_list_view(self, authenticated_client):
        """Test the vineyard list view."""
        client, _ = authenticated_client
        response = client.get(reverse('vineyards:list_vineyards'))
        assert response.status_code == 200
        assert 'vineyards/list_vineyards.html' in [t.name for t in response.templates]

    def test_vineyard_create_view(self, authenticated_client, vineyard_data):
        """Test vineyard creation."""
        client, _ = authenticated_client
        response = client.post(
            reverse('vineyards:add_vineyard'),
            data=vineyard_data
        )
        assert response.status_code == 302  # Redirect after success
        assert Vineyard.objects.count() == 1
        vineyard = Vineyard.objects.first()
        assert vineyard.name == vineyard_data['name']

    def test_vineyard_update_view(self, authenticated_client, vineyard_data):
        """Test vineyard update."""
        client, user = authenticated_client
        vineyard = Vineyard.objects.create(
            **vineyard_data,
            created_by=user
        )
        
        updated_data = vineyard_data.copy()
        updated_data['name'] = 'Updated Vineyard'
        
        response = client.post(
            reverse('vineyards:edit_vineyard', kwargs={'vineyard_id': vineyard.id}),
            data=updated_data
        )
        assert response.status_code == 302
        vineyard.refresh_from_db()
        assert vineyard.name == 'Updated Vineyard'

    def test_vineyard_delete_view(self, authenticated_client, vineyard_data):
        """Test vineyard deletion."""
        client, user = authenticated_client
        vineyard = Vineyard.objects.create(
            **vineyard_data,
            created_by=user
        )
        
        response = client.post(
            reverse('vineyards:delete_vineyard', kwargs={'vineyard_id': vineyard.id})
        )
        assert response.status_code == 302
        assert Vineyard.objects.count() == 0

    def test_vineyard_detail_view(self, authenticated_client, vineyard_data):
        """Test vineyard detail view."""
        client, user = authenticated_client
        vineyard = Vineyard.objects.create(
            **vineyard_data,
            created_by=user
        )
        
        response = client.get(
            reverse('vineyards:vineyard_detail', kwargs={'vineyard_id': vineyard.id})
        )
        assert response.status_code == 200
        assert 'vineyards/vineyard_detail.html' in [t.name for t in response.templates]
        assert response.context['vineyard'] == vineyard

@pytest.mark.django_db
class TestSupplierViews:
    """Test cases for supplier views."""

    def test_supplier_list_view(self, authenticated_client):
        """Test the supplier list view."""
        client, _ = authenticated_client
        response = client.get(reverse('vineyards:list_suppliers'))
        assert response.status_code == 200
        assert 'vineyards/list_suppliers.html' in [t.name for t in response.templates]

    def test_supplier_create_view(self, authenticated_client, supplier_data):
        """Test supplier creation."""
        client, _ = authenticated_client
        response = client.post(
            reverse('vineyards:add_supplier'),
            data=supplier_data
        )
        assert response.status_code == 302  # Redirect after success
        # Get the created supplier
        supplier = Supplier.objects.get(name=supplier_data['name'])
        assert response.url == reverse('vineyards:supplier_detail', kwargs={'supplier_id': supplier.id})

    def test_supplier_update_view(self, authenticated_client, supplier_data):
        """Test supplier update."""
        client, user = authenticated_client
        supplier = Supplier.objects.create(
            **supplier_data,
            created_by=user
        )
        
        updated_data = supplier_data.copy()
        updated_data['name'] = 'Updated Supplier'
        
        response = client.post(
            reverse('vineyards:edit_supplier', kwargs={'supplier_id': supplier.id}),
            data=updated_data
        )
        assert response.status_code == 302
        assert response.url == reverse('vineyards:supplier_detail', kwargs={'supplier_id': supplier.id})

    def test_supplier_delete_view(self, authenticated_client, supplier_data):
        """Test supplier deletion."""
        client, user = authenticated_client
        supplier = Supplier.objects.create(
            **supplier_data,
            created_by=user
        )
        
        response = client.post(
            reverse('vineyards:delete_supplier', kwargs={'supplier_id': supplier.id})
        )
        assert response.status_code == 302
        assert Supplier.objects.count() == 0

    def test_supplier_detail_view(self, authenticated_client, supplier_data):
        """Test supplier detail view."""
        client, user = authenticated_client
        supplier = Supplier.objects.create(
            **supplier_data,
            created_by=user
        )
        
        response = client.get(
            reverse('vineyards:supplier_detail', kwargs={'supplier_id': supplier.id})
        )
        assert response.status_code == 200
        assert 'vineyards/supplier_detail.html' in [t.name for t in response.templates]
        assert response.context['supplier'] == supplier

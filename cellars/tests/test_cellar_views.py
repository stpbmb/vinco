"""
Integration tests for cellar views.
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from cellars.models import Cellar, Tank

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
    for model in [Cellar, Tank]:
        content_type = ContentType.objects.get_for_model(model)
        permissions = Permission.objects.filter(content_type=content_type)
        user.user_permissions.add(*permissions)
    
    client.login(username='testuser', password='testpass123')
    return client, user

@pytest.fixture
def cellar_data():
    """Return valid cellar form data."""
    return {
        'name': 'Test Cellar',
        'location': 'Test Location',
        'capacity': 1000,
    }

@pytest.fixture
def cellar(authenticated_client):
    """Create a test cellar."""
    client, user = authenticated_client
    cellar = Cellar.objects.create(
        name='Test Cellar',
        location='Test Location',
        capacity=1000,
        created_by=user
    )
    return cellar

@pytest.fixture
def tank_data(cellar):
    """Return valid tank form data."""
    return {
        'name': 'Test Tank',
        'cellar': cellar.id,
        'tank_type': 'stainless_steel',
        'capacity': 500,
        'current_volume': 0,
    }

@pytest.fixture
def tank(cellar, authenticated_client):
    """Create a test tank."""
    _, user = authenticated_client
    return Tank.objects.create(
        name='Test Tank',
        cellar=cellar,
        tank_type='stainless_steel',
        capacity=500,
        current_volume=0,
        created_by=user
    )

@pytest.mark.django_db
class TestCellarViews:
    """Test cases for cellar views."""

    def test_cellar_list_view(self, authenticated_client):
        """Test the cellar list view."""
        client, _ = authenticated_client
        response = client.get(reverse('cellars:list_cellars'))
        assert response.status_code == 200

    def test_cellar_create_view(self, authenticated_client, cellar_data):
        """Test cellar creation."""
        client, _ = authenticated_client
        response = client.post(reverse('cellars:add_cellar'), cellar_data)
        assert response.status_code == 302
        assert Cellar.objects.count() == 1

    def test_cellar_update_view(self, authenticated_client, cellar):
        """Test cellar update."""
        client, _ = authenticated_client
        url = reverse('cellars:edit_cellar', args=[cellar.id])
        data = {
            'name': 'Updated Cellar',
            'location': 'Updated Location',
            'capacity': 2000,
        }
        response = client.post(url, data)
        assert response.status_code == 302
        cellar.refresh_from_db()
        assert cellar.name == 'Updated Cellar'

    def test_cellar_delete_view(self, authenticated_client, cellar):
        """Test cellar deletion."""
        client, _ = authenticated_client
        url = reverse('cellars:delete_cellar', args=[cellar.id])
        response = client.post(url)
        assert response.status_code == 302
        assert Cellar.objects.count() == 0

@pytest.mark.django_db
class TestTankViews:
    """Test cases for tank views."""

    def test_tank_list_view(self, authenticated_client, cellar):
        """Test the tank list view."""
        client, _ = authenticated_client
        response = client.get(reverse('cellars:list_tanks'))
        assert response.status_code == 200

    def test_tank_create_view(self, authenticated_client, tank_data, cellar):
        """Test tank creation."""
        client, _ = authenticated_client
        data = tank_data.copy()
        data['cellar'] = cellar.id
        response = client.post(
            reverse('cellars:add_tank', kwargs={'cellar_id': cellar.id}),
            data,
            follow=True
        )
        assert response.status_code == 200
        assert Tank.objects.count() == 1
        tank = Tank.objects.first()
        assert tank.cellar == cellar

    def test_tank_update_view(self, authenticated_client, tank):
        """Test tank update."""
        client, _ = authenticated_client
        # Update cellar capacity to accommodate the increased tank capacity
        tank.cellar.capacity = 2000
        tank.cellar.save()

        url = reverse('cellars:edit_tank', args=[tank.id])
        data = {
            'name': 'Updated Tank',
            'cellar': tank.cellar.id,
            'tank_type': 'stainless_steel',
            'capacity': 1000,
            'current_volume': 200,
            'notes': 'Updated notes'
        }
        response = client.post(url, data)
        assert response.status_code == 302
        tank.refresh_from_db()
        assert tank.name == 'Updated Tank'

    def test_tank_transfer(self, authenticated_client, cellar):
        """Test wine transfer between tanks."""
        client, _ = authenticated_client
        # Update cellar capacity to accommodate both tanks
        cellar.capacity = 3000
        cellar.save()

        source_tank = Tank.objects.create(
            name='Source Tank',
            cellar=cellar,
            tank_type='stainless_steel',
            capacity=1000,
            current_volume=500,
            created_by=cellar.created_by
        )
        target_tank = Tank.objects.create(
            name='Target Tank',
            cellar=cellar,
            tank_type='stainless_steel',
            capacity=1000,
            current_volume=0,
            created_by=cellar.created_by
        )
        
        data = {
            'source_tank': source_tank.id,
            'target_tank': target_tank.id,
            'volume': 300,
            'transfer_date': '2025-02-01'
        }
        response = client.post(reverse('cellars:transfer_wine'), data)
        assert response.status_code == 302
        
        source_tank.refresh_from_db()
        target_tank.refresh_from_db()
        assert source_tank.current_volume == 200
        assert target_tank.current_volume == 300

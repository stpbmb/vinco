"""
Integration tests for harvest views.
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from harvests.models import Harvest, HarvestAllocation
from cellars.models import Tank, Cellar
from vineyards.models import Vineyard

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
    for model in [Harvest, HarvestAllocation, Vineyard]:
        content_type = ContentType.objects.get_for_model(model)
        permissions = Permission.objects.filter(content_type=content_type)
        user.user_permissions.add(*permissions)
    
    client.login(username='testuser', password='testpass123')
    return client, user

@pytest.fixture
def vineyard(authenticated_client):
    """Create a test vineyard."""
    _, user = authenticated_client
    return Vineyard.objects.create(
        name='Test Vineyard',
        location='Test Location',
        size=100,
        ownership_type='owned',
        grape_variety='merlot',
        created_by=user
    )

@pytest.fixture
def harvest_data(vineyard):
    """Return valid harvest form data."""
    return {
        'vineyard': vineyard.id,
        'date': '2025-02-01',
        'quantity': 1000,
        'notes': 'Test harvest notes'
    }

@pytest.fixture
def harvest(authenticated_client, vineyard):
    """Create a test harvest."""
    _, user = authenticated_client
    return Harvest.objects.create(
        vineyard=vineyard,
        date='2025-02-01',
        quantity=1000,
        notes='Test harvest notes',
        created_by=user
    )

@pytest.fixture
def cellar(authenticated_client):
    """Create a test cellar."""
    _, user = authenticated_client
    return Cellar.objects.create(
        name='Test Cellar',
        location='Test Location',
        capacity=2000,
        created_by=user
    )

@pytest.fixture
def tank(authenticated_client, cellar):
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

@pytest.fixture
def harvest_allocation_data(harvest, tank):
    """Return valid harvest allocation form data."""
    return {
        'harvest': harvest.id,
        'tank': tank.id,
        'allocated_volume': 300,
        'allocation_date': '2025-02-01'
    }

@pytest.mark.django_db
class TestHarvestViews:
    """Test cases for harvest views."""

    def test_harvest_list_view(self, authenticated_client):
        """Test the harvest list view."""
        client, _ = authenticated_client
        response = client.get(reverse('harvests:list_harvests'))
        assert response.status_code == 200

    def test_harvest_create_view(self, authenticated_client, harvest_data):
        """Test harvest creation."""
        client, _ = authenticated_client
        response = client.post(reverse('harvests:add_harvest'), harvest_data)
        assert response.status_code == 302
        assert Harvest.objects.count() == 1

    def test_harvest_update_view(self, authenticated_client, harvest):
        """Test harvest update."""
        client, _ = authenticated_client
        url = reverse('harvests:edit_harvest', args=[harvest.id])
        data = {
            'vineyard': harvest.vineyard_id,
            'date': '2025-02-02',
            'quantity': 2000,
            'notes': 'Updated harvest notes'
        }
        response = client.post(url, data)
        assert response.status_code == 302
        harvest.refresh_from_db()
        assert harvest.quantity == 2000

    def test_harvest_delete_view(self, authenticated_client, harvest):
        """Test harvest deletion."""
        client, _ = authenticated_client
        url = reverse('harvests:delete_harvest', args=[harvest.id])
        response = client.post(url)
        assert response.status_code == 302
        assert Harvest.objects.count() == 0

@pytest.mark.django_db
class TestHarvestAllocationViews:
    """Test cases for harvest allocation views."""

    def test_harvest_allocation_list_view(self, authenticated_client):
        """Test the harvest allocation list view."""
        client, _ = authenticated_client
        response = client.get(reverse('harvests:list_allocations'))
        assert response.status_code == 200

    def test_harvest_allocation_create_view(self, authenticated_client, harvest, harvest_allocation_data):
        """Test harvest allocation creation."""
        client, _ = authenticated_client
        response = client.post(
            reverse('harvests:allocation_create'),
            harvest_allocation_data
        )
        assert response.status_code == 302
        assert HarvestAllocation.objects.count() == 1
        allocation = HarvestAllocation.objects.first()
        assert allocation.harvest == harvest
        assert allocation.allocated_volume == harvest_allocation_data['allocated_volume']

    def test_harvest_allocation_validation(self, authenticated_client, harvest, tank):
        """Test harvest allocation validation in view."""
        client, _ = authenticated_client
        data = {
            'harvest': harvest.id,
            'tank': tank.id,
            'allocated_volume': 1200,  # More than harvest quantity
            'allocation_date': '2025-02-01'
        }
        response = client.post(reverse('harvests:allocation_create'), data)
        assert response.status_code == 400
        assert HarvestAllocation.objects.count() == 0

    def test_multiple_allocations(self, authenticated_client, harvest, tank):
        """Test creating multiple allocations for the same harvest."""
        client, _ = authenticated_client

        # Create first allocation
        data1 = {
            'harvest': harvest.id,
            'tank': tank.id,
            'allocated_volume': 400,
            'allocation_date': '2025-02-01'
        }
        response1 = client.post(reverse('harvests:allocation_create'), data1)
        assert response1.status_code == 302
        assert HarvestAllocation.objects.count() == 1

        # Create second allocation
        data2 = {
            'harvest': harvest.id,
            'tank': tank.id,
            'allocated_volume': 400,
            'allocation_date': '2025-02-01'
        }
        response2 = client.post(reverse('harvests:allocation_create'), data2)
        assert response2.status_code == 302
        assert HarvestAllocation.objects.count() == 2

        # Verify total allocated volume
        total_allocated = HarvestAllocation.objects.filter(harvest=harvest).aggregate(
            total=models.Sum('allocated_volume'))['total']
        assert total_allocated == 800

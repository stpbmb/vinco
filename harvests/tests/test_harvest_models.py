"""
Unit tests for harvest models.
"""

import pytest
from datetime import date
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from harvests.models import Harvest, HarvestAllocation
from vineyards.models import Vineyard
from cellars.models import Cellar, Tank

User = get_user_model()

@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def vineyard(user):
    """Create a test vineyard."""
    return Vineyard.objects.create(
        name="Test Vineyard",
        location="Test Location",
        ownership_type="owned",
        size=1.0,
        grape_variety="merlot",
        created_by=user
    )

@pytest.fixture
def cellar(user):
    """Create a test cellar."""
    return Cellar.objects.create(
        name="Test Cellar",
        location="Test Location",
        capacity=2000,
        created_by=user
    )

@pytest.fixture
def tank(cellar, user):
    """Create a test tank."""
    return Tank.objects.create(
        name="Test Tank",
        cellar=cellar,
        tank_type="stainless_steel",
        capacity=1000,
        current_volume=0,
        created_by=user
    )

@pytest.fixture
def harvest(vineyard, user):
    """Create a test harvest."""
    return Harvest.objects.create(
        vineyard=vineyard,
        date="2025-02-01",
        quantity=1000,  # 1000 kg
        juice_yield=0.75,  # 75% juice yield
        created_by=user
    )

@pytest.fixture
def harvest_allocation(harvest, tank, user):
    """Create a test harvest allocation."""
    return HarvestAllocation.objects.create(
        harvest=harvest,
        tank=tank,
        allocated_volume=300,
        allocation_date='2025-02-01',
        created_by=user
    )

@pytest.mark.django_db
class TestHarvestModel:
    """Test cases for the Harvest model."""

    def test_harvest_creation(self, harvest):
        """Test that a harvest can be created with valid data."""
        assert harvest.pk is not None
        assert harvest.quantity == 1000
        assert harvest.juice_yield == 0.75
        assert harvest.available_juice == 750  # 1000kg * 0.75 = 750L

    def test_harvest_str(self, harvest):
        """Test the string representation of a harvest."""
        expected = f'Harvest on {harvest.date} from {harvest.vineyard.name}'
        assert str(harvest) == expected

    def test_harvest_quantity_validation(self, harvest, tank, user):
        """Test that harvest quantity cannot be reduced below allocated amount."""
        # Create an allocation
        HarvestAllocation.objects.create(
            harvest=harvest,
            tank=tank,
            allocated_volume=300,  # 300L out of 750L available
            allocation_date='2025-02-01',
            created_by=user
        )
        
        # Try to reduce harvest quantity below allocated amount
        harvest.quantity = 200  # 200kg * 0.75 = 150L < 300L allocated
        with pytest.raises(ValidationError) as excinfo:
            harvest.full_clean()
        assert "Cannot reduce harvest quantity below already allocated volume" in str(excinfo.value)

    def test_harvest_available_quantity(self, harvest, tank, user):
        """Test calculation of available juice quantity."""
        # Initially all juice is available
        assert harvest.available_juice == 750  # 1000kg * 0.75 = 750L
        
        # Create an allocation for 300L
        HarvestAllocation.objects.create(
            harvest=harvest,
            tank=tank,
            allocated_volume=300,
            allocation_date='2025-02-01',
            created_by=user
        )
        
        # Check remaining juice
        assert harvest.available_juice == 450  # 750L - 300L = 450L

@pytest.mark.django_db
class TestHarvestAllocationModel:
    """Test cases for the HarvestAllocation model."""

    def test_harvest_allocation_creation(self, harvest, tank, user):
        """Test that a harvest allocation can be created with valid data."""
        allocation = HarvestAllocation.objects.create(
            harvest=harvest,
            tank=tank,
            allocated_volume=300,  # 300L out of 750L available
            allocation_date='2025-02-01',
            created_by=user
        )
        assert allocation.pk is not None
        assert allocation.allocated_volume == 300

    def test_harvest_allocation_str(self, harvest, tank, user):
        """Test the string representation of a harvest allocation."""
        allocation = HarvestAllocation.objects.create(
            harvest=harvest,
            tank=tank,
            allocated_volume=300,
            allocation_date='2025-02-01',
            created_by=user
        )
        expected = f'300.0L from {harvest} to {tank}'
        assert str(allocation) == expected

    def test_harvest_allocation_validation(self, harvest, tank, user):
        """Test validation of allocation volume against available juice."""
        # Try to allocate more than available juice
        with pytest.raises(ValidationError) as excinfo:
            HarvestAllocation.objects.create(
                harvest=harvest,
                tank=tank,
                allocated_volume=800,  # More than 750L available
                allocation_date='2025-02-01',
                created_by=user
            )
        assert "Cannot allocate more than available juice" in str(excinfo.value)

    def test_tank_capacity_validation(self, harvest, tank, user):
        """Test validation of allocation volume against tank capacity."""
        # Try to allocate more than tank capacity
        with pytest.raises(ValidationError) as excinfo:
            HarvestAllocation.objects.create(
                harvest=harvest,
                tank=tank,
                allocated_volume=1200,  # More than 1000L tank capacity
                allocation_date='2025-02-01',
                created_by=user
            )
        assert "Allocation would exceed tank capacity" in str(excinfo.value)

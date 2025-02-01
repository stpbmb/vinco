"""
Unit tests for cellar models.
"""

import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from cellars.models import Cellar, Tank

User = get_user_model()

@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def cellar(user):
    """Create a test cellar."""
    return Cellar.objects.create(
        name='Test Cellar',
        capacity=1000,
        location='Test Location',
        created_by=user
    )

@pytest.fixture
def tank(cellar):
    """Create a test tank."""
    return Tank.objects.create(
        name='Test Tank',
        cellar=cellar,
        tank_type='stainless_steel',
        capacity=100,
        current_volume=0,
        created_by=cellar.created_by
    )

@pytest.mark.django_db
class TestCellarModel:
    """Test cases for the Cellar model."""

    def test_cellar_creation(self, cellar):
        """Test cellar instance creation."""
        assert cellar.name == 'Test Cellar'
        assert cellar.capacity == 1000
        assert cellar.location == 'Test Location'

    def test_cellar_str(self, cellar):
        """Test cellar string representation."""
        assert str(cellar) == 'Test Cellar'

    def test_cellar_capacity_validation(self, cellar, tank):
        """Test cellar capacity validation."""
        # Try to reduce capacity below total tank capacity
        cellar.capacity = 50
        with pytest.raises(ValidationError):
            cellar.full_clean()

@pytest.mark.django_db
class TestTankModel:
    """Test cases for the Tank model."""

    def test_tank_creation(self, tank):
        """Test tank instance creation."""
        assert tank.name == 'Test Tank'
        assert tank.capacity == 100
        assert tank.current_volume == 0

    def test_tank_str(self, tank):
        """Test tank string representation."""
        assert str(tank) == 'Test Tank (Stainless Steel) in Test Cellar'

    def test_tank_capacity_validation(self, tank):
        """Test tank capacity validation."""
        tank.current_volume = 50
        tank.capacity = 40  # Try to reduce capacity below current volume
        with pytest.raises(ValidationError):
            tank.full_clean()

    def test_tank_volume_validation(self, tank):
        """Test tank volume validation."""
        tank.current_volume = 150  # Try to set volume above capacity
        with pytest.raises(ValidationError):
            tank.full_clean()

    def test_tank_available_space(self, tank):
        """Test tank available space calculation."""
        tank.current_volume = 30
        assert tank.available_space == 70

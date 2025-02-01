"""
Unit tests for vineyard models.
"""

import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from vineyards.models import Vineyard, Supplier

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
def supplier(user):
    """Create a test supplier."""
    return Supplier.objects.create(
        name='Test Supplier',
        address='Test Address',
        oib='12345678901',
        created_by=user
    )

@pytest.fixture
def vineyard(user):
    """Create a test vineyard."""
    return Vineyard.objects.create(
        name='Test Vineyard',
        location='Test Location',
        grape_variety='merlot',
        size=1.0,
        ownership_type='owned',
        created_by=user
    )

@pytest.mark.django_db
class TestVineyardModel:
    """Test cases for the Vineyard model."""

    def test_vineyard_creation(self, vineyard):
        """Test vineyard instance creation."""
        assert vineyard.name == 'Test Vineyard'
        assert vineyard.location == 'Test Location'
        assert vineyard.grape_variety == 'merlot'
        assert vineyard.size == 1.0
        assert vineyard.ownership_type == 'owned'
        assert str(vineyard) == 'Test Vineyard - Merlot'

    def test_vineyard_with_supplier(self, vineyard, supplier):
        """Test vineyard with supplier relationship."""
        vineyard.ownership_type = 'supplied'
        vineyard.supplier = supplier
        vineyard.save()
        
        assert vineyard.supplier == supplier
        assert vineyard in supplier.vineyards.all()

    def test_vineyard_area_validation(self, vineyard):
        """Test vineyard area validation."""
        with pytest.raises(ValidationError):
            vineyard.size = -1.0
            vineyard.full_clean()

    def test_vineyard_spacing_validation(self, vineyard):
        """Test vineyard spacing validation."""
        pass

    def test_vineyard_ownership_validation(self, vineyard):
        """Test vineyard ownership type validation."""
        vineyard.ownership_type = 'supplied'
        with pytest.raises(ValidationError):
            vineyard.full_clean()  # Should fail without supplier

        vineyard.supplier = None
        with pytest.raises(ValidationError):
            vineyard.full_clean()

@pytest.mark.django_db
class TestSupplierModel:
    """Test cases for the Supplier model."""

    def test_supplier_creation(self, supplier):
        """Test supplier instance creation."""
        assert supplier.name == 'Test Supplier'
        assert supplier.address == 'Test Address'
        assert supplier.oib == '12345678901'
        assert str(supplier) == 'Test Supplier'

    def test_supplier_email_validation(self, supplier):
        """Test supplier email validation."""
        pass

    def test_supplier_phone_validation(self, supplier):
        """Test supplier phone validation."""
        pass

    def test_supplier_vineyards_relation(self, supplier, vineyard):
        """Test supplier-vineyard relationship."""
        vineyard.ownership_type = 'supplied'
        vineyard.supplier = supplier
        vineyard.save()

        assert vineyard in supplier.vineyards.all()
        assert supplier.vineyards.count() == 1

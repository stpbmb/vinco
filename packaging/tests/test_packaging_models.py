"""
Unit tests for packaging models.
"""

import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from packaging.models import Bottle, Label, Closure, Box

User = get_user_model()

@pytest.fixture
def test_user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def bottle(test_user):
    """Create a test bottle."""
    return Bottle.objects.create(
        name='Test Bottle',
        bottle_type='bordeaux',
        volume=750,
        stock=100,
        minimum_stock=10,
        height=300,  # mm
        diameter=80,  # mm
        weight=500,  # g
        glass_color='clear',
        created_by=test_user
    )

@pytest.fixture
def label(user):
    """Create a test label."""
    return Label.objects.create(
        name='Test Label',
        label_type='front',
        width=100,
        height=150,
        material='paper',
        supplier='Test Supplier',
        price=0.50,
        stock=1000,
        minimum_stock=100,
        created_by=user
    )

@pytest.fixture
def closure(user):
    """Create a test closure."""
    return Closure.objects.create(
        name='Test Closure',
        closure_type='cork_natural',
        material='cork',
        color='Natural',
        diameter=24,
        height=44,
        stock=1000,
        minimum_stock=100,
        created_by=user
    )

@pytest.fixture
def box(user):
    """Create a test box."""
    return Box.objects.create(
        name='Test Box',
        box_type='six_pack',
        material='cardboard',
        bottle_capacity=6,
        length=300,
        width=200,
        height=350,
        weight=200,
        stock=500,
        minimum_stock=50,
        created_by=user
    )

@pytest.mark.django_db
class TestBottleModel:
    """Test cases for the Bottle model."""

    def test_bottle_creation(self, test_user):
        """Test creating a bottle."""
        bottle = Bottle.objects.create(
            name='Test Bottle',
            bottle_type='bordeaux',
            volume=750,
            glass_color='clear',
            height=300,  # mm
            diameter=80,  # mm
            weight=500,  # g
            stock=100,
            minimum_stock=10,
            created_by=test_user
        )
        assert bottle.name == 'Test Bottle'
        assert bottle.volume == 750
        assert bottle.stock == 100

    def test_bottle_str(self, bottle):
        """Test bottle string representation."""
        assert str(bottle) == f"{bottle.name} ({bottle.volume}ml {bottle.get_bottle_type_display()})"

    def test_bottle_quantity_validation(self, bottle):
        """Test bottle quantity validation."""
        bottle.stock = -10
        with pytest.raises(ValidationError):
            bottle.save()

@pytest.mark.django_db
class TestLabelModel:
    """Test cases for the Label model."""

    def test_label_creation(self, label):
        """Test label instance creation."""
        assert label.name == 'Test Label'
        assert label.width == 100
        assert label.height == 150
        assert label.material == 'paper'
        assert label.supplier == 'Test Supplier'
        assert label.price == 0.50
        assert label.stock == 1000
        assert label.minimum_stock == 100

    def test_label_str(self, label):
        """Test label string representation."""
        assert str(label) == f"{label.name} ({label.get_label_type_display()})"

    def test_label_quantity_validation(self, label):
        """Test label quantity validation."""
        label.stock = -10
        with pytest.raises(ValidationError):
            label.save()

@pytest.mark.django_db
class TestClosureModel:
    """Test cases for the Closure model."""

    def test_closure_creation(self, closure):
        """Test closure instance creation."""
        assert closure.name == 'Test Closure'
        assert closure.closure_type == 'cork_natural'
        assert closure.material == 'cork'
        assert closure.color == 'Natural'
        assert closure.diameter == 24
        assert closure.height == 44
        assert closure.stock == 1000
        assert closure.minimum_stock == 100

    def test_closure_str(self, closure):
        """Test closure string representation."""
        assert str(closure) == f"{closure.name} ({closure.get_closure_type_display()})"

    def test_closure_quantity_validation(self, closure):
        """Test closure quantity validation."""
        closure.stock = -10
        with pytest.raises(ValidationError):
            closure.save()

@pytest.mark.django_db
class TestBoxModel:
    """Test cases for the Box model."""

    def test_box_creation(self, box):
        """Test box instance creation."""
        assert box.name == 'Test Box'
        assert box.box_type == 'six_pack'
        assert box.material == 'cardboard'
        assert box.bottle_capacity == 6
        assert box.length == 300
        assert box.width == 200
        assert box.height == 350
        assert box.weight == 200
        assert box.stock == 500
        assert box.minimum_stock == 50

    def test_box_str(self, box):
        """Test box string representation."""
        assert str(box) == f"{box.name} ({box.get_box_type_display()} - {box.bottle_capacity} bottles)"

    def test_box_capacity_validation(self, box):
        """Test box capacity validation."""
        box.bottle_capacity = 0
        with pytest.raises(ValidationError):
            box.save()

    def test_box_quantity_validation(self, box):
        """Test box quantity validation."""
        box.stock = -10
        with pytest.raises(ValidationError):
            box.save()

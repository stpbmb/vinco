"""
Integration tests for packaging views.
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from packaging.models import Bottle, Label, Closure, Box, Bottling
from cellars.models import Tank, Cellar

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
    for model in [Bottle, Label, Closure, Box, Tank, Cellar, Bottling]:
        content_type = ContentType.objects.get_for_model(model)
        permissions = Permission.objects.filter(content_type=content_type)
        user.user_permissions.add(*permissions)
    
    client.login(username='testuser', password='testpass123')
    return client, user

@pytest.fixture
def bottle_data():
    """Return valid bottle form data."""
    return {
        'name': 'Test Bottle',
        'bottle_type': 'bordeaux',
        'volume': 750,
        'glass_color': 'green',
        'height': 300,
        'diameter': 80,
        'weight': 500,
        'supplier': 'Test Supplier',
        'price': '10.00',
        'stock': 1000,
        'minimum_stock': 200,
        'notes': 'Test bottle'
    }

@pytest.fixture
def label_data():
    """Return valid label form data."""
    return {
        'name': 'Test Label',
        'label_type': 'front',
        'material': 'paper',
        'width': 100,
        'height': 150,
        'supplier': 'Test Supplier',
        'price': '0.50',
        'stock': 1000,
        'minimum_stock': 200,
        'notes': 'Test label'
    }

@pytest.fixture
def closure_data():
    """Return valid closure form data."""
    return {
        'name': 'Test Closure',
        'closure_type': 'cork_natural',
        'material': 'cork',
        'color': 'natural',
        'diameter': 24,
        'height': 44,
        'supplier': 'Test Supplier',
        'price': '1.00',
        'stock': 1000,
        'minimum_stock': 200,
        'notes': 'Test closure'
    }

@pytest.fixture
def box_data():
    """Return valid box form data."""
    return {
        'name': 'Test Box',
        'box_type': 'twelve_pack',
        'material': 'cardboard',
        'bottle_capacity': 12,
        'length': 400,
        'width': 300,
        'height': 200,
        'weight': 500,
        'supplier': 'Test Supplier',
        'price': '5.00',
        'stock': 100,
        'minimum_stock': 20,
        'notes': 'Test box'
    }

@pytest.fixture
def cellar_data():
    """Return valid cellar form data."""
    return {
        'name': 'Test Cellar',
        'location': 'Test Location',
        'capacity': 10000,
        'notes': 'Test cellar'
    }

@pytest.mark.django_db
class TestBottleViews:
    """Test cases for bottle views."""

    def test_bottle_list_view(self, authenticated_client):
        """Test the bottle list view."""
        client, _ = authenticated_client
        response = client.get(reverse('packaging:list_bottles'))
        assert response.status_code == 200

    def test_bottle_create_view(self, authenticated_client, bottle_data):
        """Test bottle creation."""
        client, _ = authenticated_client
        response = client.post(reverse('packaging:add_bottle'), bottle_data)
        assert response.status_code == 302
        assert Bottle.objects.count() == 1

    def test_bottle_update_view(self, authenticated_client, bottle_data):
        """Test bottle update."""
        client, _ = authenticated_client
        bottle = Bottle.objects.create(
            **bottle_data,
            created_by=authenticated_client[1]
        )
        url = reverse('packaging:edit_bottle', args=[bottle.id])
        data = bottle_data.copy()
        data['stock'] = 2000
        response = client.post(url, data)
        assert response.status_code == 302
        bottle.refresh_from_db()
        assert bottle.stock == 2000

@pytest.mark.django_db
class TestLabelViews:
    """Test cases for label views."""

    def test_label_list_view(self, authenticated_client):
        """Test the label list view."""
        client, _ = authenticated_client
        response = client.get(reverse('packaging:list_labels'))
        assert response.status_code == 200

    def test_label_create_view(self, authenticated_client, label_data):
        """Test label creation."""
        client, _ = authenticated_client
        response = client.post(reverse('packaging:add_label'), label_data)
        assert response.status_code == 302
        assert Label.objects.count() == 1

@pytest.mark.django_db
class TestClosureViews:
    """Test cases for closure views."""

    def test_closure_list_view(self, authenticated_client):
        """Test the closure list view."""
        client, _ = authenticated_client
        response = client.get(reverse('packaging:list_closures'))
        assert response.status_code == 200

    def test_closure_create_view(self, authenticated_client, closure_data):
        """Test closure creation."""
        client, _ = authenticated_client
        response = client.post(reverse('packaging:add_closure'), closure_data)
        assert response.status_code == 302
        assert Closure.objects.count() == 1

@pytest.mark.django_db
class TestBoxViews:
    """Test cases for box views."""

    def test_box_list_view(self, authenticated_client):
        """Test the box list view."""
        client, _ = authenticated_client
        response = client.get(reverse('packaging:list_boxes'))
        assert response.status_code == 200

    def test_box_create_view(self, authenticated_client, box_data):
        """Test box creation."""
        client, _ = authenticated_client
        response = client.post(reverse('packaging:add_box'), box_data)
        assert response.status_code == 302
        assert Box.objects.count() == 1

    def test_box_capacity_validation(self, authenticated_client, box_data):
        """Test box capacity validation."""
        client, _ = authenticated_client
        data = box_data.copy()
        data['bottle_capacity'] = 0  # Invalid capacity
        response = client.post(reverse('packaging:add_box'), data)
        assert response.status_code == 400
        assert Box.objects.count() == 0

@pytest.mark.django_db
class TestBottlingViews:
    """Test cases for bottling views."""

    def test_bottling_create_view(self, authenticated_client, bottle_data, label_data, closure_data, box_data, cellar_data):
        """Test bottling creation."""
        client, user = authenticated_client

        # Create required objects
        bottle = Bottle.objects.create(**bottle_data, created_by=user)
        label = Label.objects.create(**label_data, created_by=user)
        closure = Closure.objects.create(**closure_data, created_by=user)
        box = Box.objects.create(**box_data, created_by=user)
        cellar = Cellar.objects.create(**cellar_data, created_by=user)
        tank = Tank.objects.create(
            name="Test Tank",
            tank_type="stainless_steel",
            capacity=1000,
            current_volume=500,
            cellar=cellar,
            created_by=user
        )

        data = {
            'tank': tank.id,
            'bottle': bottle.id,
            'label': label.id,
            'closure': closure.id,
            'box': box.id,
            'bottling_date': '2025-01-01',
            'quantity': 100,
            'status': 'unfinished'
        }
        response = client.post(reverse('packaging:add_bottling'), data)
        assert response.status_code == 302

    def test_bottling_validation(self, authenticated_client, bottle_data, label_data, closure_data, box_data, cellar_data):
        """Test bottling validation."""
        client, user = authenticated_client

        # Create required objects with low stock
        bottle = Bottle.objects.create(**{**bottle_data, 'stock': 50}, created_by=user)
        label = Label.objects.create(**{**label_data, 'stock': 50}, created_by=user)
        closure = Closure.objects.create(**{**closure_data, 'stock': 50}, created_by=user)
        box = Box.objects.create(**{**box_data, 'stock': 5}, created_by=user)
        cellar = Cellar.objects.create(**cellar_data, created_by=user)
        tank = Tank.objects.create(
            name="Test Tank",
            tank_type="stainless_steel",
            capacity=1000,
            current_volume=500,
            cellar=cellar,
            created_by=user
        )

        # Try to create a bottling with quantity that exceeds available stock
        data = {
            'tank': tank.id,
            'bottle': bottle.id,
            'label': label.id,
            'closure': closure.id,
            'box': box.id,
            'bottling_date': '2025-01-01',
            'quantity': 1000,  # More than available stock
            'status': 'unfinished'
        }
        response = client.post(reverse('packaging:add_bottling'), data)
        assert response.status_code == 400

    def test_bottling_list_unfinished(self, authenticated_client, bottle_data, label_data, closure_data, box_data, cellar_data):
        """Test listing unfinished bottlings."""
        client, user = authenticated_client

        # Create required objects
        bottle = Bottle.objects.create(**bottle_data, created_by=user)
        label = Label.objects.create(**label_data, created_by=user)
        closure = Closure.objects.create(**closure_data, created_by=user)
        box = Box.objects.create(**box_data, created_by=user)
        cellar = Cellar.objects.create(**cellar_data, created_by=user)
        tank = Tank.objects.create(
            name="Test Tank",
            tank_type="stainless_steel",
            capacity=1000,
            current_volume=500,
            cellar=cellar,
            created_by=user
        )

        # Create an unfinished bottling
        bottling = Bottling.objects.create(
            tank=tank,
            bottle=bottle,
            label=label,
            closure=closure,
            box=box,
            bottling_date='2025-01-01',
            quantity=100,
            status='unfinished',
            created_by=user
        )

        response = client.get(reverse('packaging:list_unfinished'))
        assert response.status_code == 200
        assert 'bottlings' in response.context
        assert len(response.context['bottlings']) == 1
        assert response.context['bottlings'][0] == bottling

    def test_bottling_list_finished(self, authenticated_client, bottle_data, label_data, closure_data, box_data, cellar_data):
        """Test listing finished bottlings."""
        client, user = authenticated_client

        # Create required objects
        bottle = Bottle.objects.create(**bottle_data, created_by=user)
        label = Label.objects.create(**label_data, created_by=user)
        closure = Closure.objects.create(**closure_data, created_by=user)
        box = Box.objects.create(**box_data, created_by=user)
        cellar = Cellar.objects.create(**cellar_data, created_by=user)
        tank = Tank.objects.create(
            name="Test Tank",
            tank_type="stainless_steel",
            capacity=1000,
            current_volume=500,
            cellar=cellar,
            created_by=user
        )

        # Create a finished bottling
        bottling = Bottling.objects.create(
            tank=tank,
            bottle=bottle,
            label=label,
            closure=closure,
            box=box,
            bottling_date='2025-01-01',
            quantity=100,
            status='finished',
            created_by=user
        )

        response = client.get(reverse('packaging:list_finished'))
        assert response.status_code == 200
        assert 'bottlings' in response.context
        assert len(response.context['bottlings']) == 1
        assert response.context['bottlings'][0] == bottling

    def test_bottling_detail(self, authenticated_client, bottle_data, label_data, closure_data, box_data, cellar_data):
        """Test viewing bottling details."""
        client, user = authenticated_client

        # Create required objects
        bottle = Bottle.objects.create(**bottle_data, created_by=user)
        label = Label.objects.create(**label_data, created_by=user)
        closure = Closure.objects.create(**closure_data, created_by=user)
        box = Box.objects.create(**box_data, created_by=user)
        cellar = Cellar.objects.create(**cellar_data, created_by=user)
        tank = Tank.objects.create(
            name="Test Tank",
            tank_type="stainless_steel",
            capacity=1000,
            current_volume=500,
            cellar=cellar,
            created_by=user
        )

        # Create a bottling
        bottling = Bottling.objects.create(
            tank=tank,
            bottle=bottle,
            label=label,
            closure=closure,
            box=box,
            bottling_date='2025-01-01',
            quantity=100,
            status='unfinished',
            created_by=user
        )

        response = client.get(reverse('packaging:bottling_detail', kwargs={'pk': bottling.pk}))
        assert response.status_code == 200
        assert response.context['bottling'] == bottling

    def test_bottling_update(self, authenticated_client, bottle_data, label_data, closure_data, box_data, cellar_data):
        """Test updating a bottling."""
        client, user = authenticated_client

        # Create required objects
        bottle = Bottle.objects.create(**bottle_data, created_by=user)
        label = Label.objects.create(**label_data, created_by=user)
        closure = Closure.objects.create(**closure_data, created_by=user)
        box = Box.objects.create(**box_data, created_by=user)
        cellar = Cellar.objects.create(**cellar_data, created_by=user)
        tank = Tank.objects.create(
            name="Test Tank",
            tank_type="stainless_steel",
            capacity=1000,
            current_volume=500,
            cellar=cellar,
            created_by=user
        )

        # Create a bottling
        bottling = Bottling.objects.create(
            tank=tank,
            bottle=bottle,
            label=label,
            closure=closure,
            box=box,
            bottling_date='2025-01-01',
            quantity=100,
            status='unfinished',
            created_by=user
        )

        # Update the bottling
        data = {
            'tank': tank.id,
            'bottle': bottle.id,
            'label': label.id,
            'closure': closure.id,
            'box': box.id,
            'bottling_date': '2025-02-01',
            'quantity': 150,
            'status': 'unfinished'
        }
        response = client.post(reverse('packaging:edit_bottling', kwargs={'pk': bottling.pk}), data)
        assert response.status_code == 302

        # Verify the update
        bottling.refresh_from_db()
        assert str(bottling.bottling_date) == '2025-02-01'
        assert bottling.quantity == 150

    def test_bottling_update_validation(self, authenticated_client, bottle_data, label_data, closure_data, box_data, cellar_data):
        """Test validation when updating a bottling."""
        client, user = authenticated_client

        # Create required objects with low stock
        bottle = Bottle.objects.create(**{**bottle_data, 'stock': 100}, created_by=user)
        label = Label.objects.create(**{**label_data, 'stock': 100}, created_by=user)
        closure = Closure.objects.create(**{**closure_data, 'stock': 100}, created_by=user)
        box = Box.objects.create(**{**box_data, 'stock': 10}, created_by=user)
        cellar = Cellar.objects.create(**cellar_data, created_by=user)
        tank = Tank.objects.create(
            name="Test Tank",
            tank_type="stainless_steel",
            capacity=1000,
            current_volume=500,
            cellar=cellar,
            created_by=user
        )

        # Create a bottling with initial quantity
        bottling = Bottling.objects.create(
            tank=tank,
            bottle=bottle,
            label=label,
            closure=closure,
            box=box,
            bottling_date='2025-01-01',
            quantity=50,
            status='unfinished',
            created_by=user
        )

        # Try to update with quantity that exceeds available stock
        data = {
            'tank': tank.id,
            'bottle': bottle.id,
            'label': label.id,
            'closure': closure.id,
            'box': box.id,
            'bottling_date': '2025-02-01',
            'quantity': 200,  # More than available stock
            'status': 'unfinished'
        }
        response = client.post(reverse('packaging:edit_bottling', kwargs={'pk': bottling.pk}), data)
        assert response.status_code == 400  # Bad request due to validation error

        # Verify the bottling wasn't updated
        bottling.refresh_from_db()
        assert str(bottling.bottling_date) == '2025-01-01'
        assert bottling.quantity == 50

    def test_bottling_delete(self, authenticated_client, bottle_data, label_data, closure_data, box_data, cellar_data):
        """Test deleting a bottling."""
        client, user = authenticated_client

        # Create required objects
        bottle = Bottle.objects.create(**bottle_data, created_by=user)
        label = Label.objects.create(**label_data, created_by=user)
        closure = Closure.objects.create(**closure_data, created_by=user)
        box = Box.objects.create(**box_data, created_by=user)
        cellar = Cellar.objects.create(**cellar_data, created_by=user)
        tank = Tank.objects.create(
            name="Test Tank",
            tank_type="stainless_steel",
            capacity=1000,
            current_volume=500,
            cellar=cellar,
            created_by=user
        )

        # Create a bottling
        bottling = Bottling.objects.create(
            tank=tank,
            bottle=bottle,
            label=label,
            closure=closure,
            box=box,
            bottling_date='2025-01-01',
            quantity=100,
            status='unfinished',
            created_by=user
        )

        # Delete the bottling
        response = client.post(reverse('packaging:delete_bottling', kwargs={'pk': bottling.pk}))
        assert response.status_code == 302
        assert not Bottling.objects.filter(pk=bottling.pk).exists()

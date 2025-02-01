from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Bottle, Box, Label, Closure
from cellars.models import Tank, Cellar
from core.utils.exceptions import InvalidOperationError, ResourceNotFoundError

class PackagingTestCase(TestCase):
    """Test case for packaging operations."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        # Create test bottle
        self.bottle = Bottle.objects.create(
            name='Test Bottle',
            bottle_type='bordeaux',
            volume=750,
            glass_color='clear',
            height=300,  # mm
            diameter=80,  # mm
            weight=500,  # g
            stock=100,
            minimum_stock=10,
            created_by=self.user
        )
        self.label = Label.objects.create(
            name='Test Label',
            label_type='front',
            material='paper',
            width=100,  # mm
            height=150,  # mm
            stock=100,
            minimum_stock=10,
            created_by=self.user
        )
        self.closure = Closure.objects.create(
            name='Test Closure',
            closure_type='cork_natural',
            material='cork',
            color='natural',
            diameter=24,  # mm
            height=40,  # mm
            stock=100,
            minimum_stock=10,
            created_by=self.user
        )
        self.box = Box.objects.create(
            name='Test Box',
            box_type='six_pack',
            material='cardboard',
            length=300,  # mm
            width=200,  # mm
            height=150,  # mm
            weight=200,  # g
            bottle_capacity=6,
            stock=100,
            minimum_stock=10,
            created_by=self.user
        )
        
        # Create test cellar and tank
        self.cellar = Cellar.objects.create(
            name='Test Cellar',
            location='Test Location',
            capacity=10000,  # liters
            created_by=self.user
        )
        self.tank = Tank.objects.create(
            cellar=self.cellar,
            name='Test Tank',
            tank_type='stainless_steel',
            capacity=1000,  # liters
            current_volume=800,  # liters, enough for testing
            created_by=self.user
        )

    def test_bottle_quantity_validation(self):
        """Test bottle quantity validation"""
        url = reverse('packaging:edit_bottle', args=[self.bottle.id])
        response = self.client.post(url, {
            'name': 'Test Bottle',
            'bottle_type': 'bordeaux',
            'volume': 750,
            'glass_color': 'clear',
            'height': 300,
            'diameter': 80,
            'weight': 500,
            'stock': -10  # Invalid negative quantity
        })
        self.assertEqual(response.status_code, 400)  # Form validation errors return 400
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('Stock cannot be negative', str(form.errors))

    def test_box_capacity_validation(self):
        """Test box capacity validation"""
        url = reverse('packaging:edit_box', args=[self.box.id])
        response = self.client.post(url, {
            'name': 'Test Box',
            'box_type': 'six_pack',
            'material': 'cardboard',
            'bottle_capacity': 0,  # Invalid zero capacity
            'length': 300,
            'width': 200,
            'height': 150,
            'weight': 200,
            'stock': 100
        })
        self.assertEqual(response.status_code, 400)  # Form validation errors return 400
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('Bottle capacity must be greater than zero', str(form.errors))

    def test_resource_not_found(self):
        """Test handling of non-existent resources"""
        url = reverse('packaging:bottle_detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_packaging_set_validation(self):
        """Test validation of complete packaging set"""
        url = reverse('packaging:add_bottling')

        # Try to create set with insufficient quantities
        response = self.client.post(url, {
            'tank': self.tank.id,
            'bottle': self.bottle.id,
            'label': self.label.id,
            'closure': self.closure.id,
            'box': self.box.id,
            'quantity': 2000,  # More than available components
            'bottling_date': '2025-02-01'
        })
        self.assertEqual(response.status_code, 400)  # Form validation errors return 400
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('Not enough wine in tank', str(form.errors))  # Tank volume is checked first

        # Valid packaging set creation
        response = self.client.post(url, {
            'tank': self.tank.id,
            'bottle': self.bottle.id,
            'label': self.label.id,
            'closure': self.closure.id,
            'box': self.box.id,
            'quantity': 50,
            'bottling_date': '2025-02-01'
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success

    def test_concurrent_operations(self):
        """Test handling of concurrent operations on the same resources"""
        url = reverse('packaging:add_bottling')
        
        # Create two packaging sets simultaneously
        response1 = self.client.post(url, {
            'tank': self.tank.id,
            'bottle': self.bottle.id,
            'label': self.label.id,
            'closure': self.closure.id,
            'box': self.box.id,
            'quantity': 50,
            'bottling_date': '2025-02-01'
        })
        response2 = self.client.post(url, {
            'tank': self.tank.id,
            'bottle': self.bottle.id,
            'label': self.label.id,
            'closure': self.closure.id,
            'box': self.box.id,
            'quantity': 700,  # Would exceed available quantities
            'bottling_date': '2025-02-01'
        })
        
        self.assertEqual(response1.status_code, 302)  # First request succeeds
        self.assertEqual(response2.status_code, 400)  # Second request fails validation
        form = response2.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('Not enough bottles in stock', str(form.errors))

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Cellar, Tank
from core.utils.exceptions import InvalidOperationError, ResourceNotFoundError

User = get_user_model()

class CellarTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.cellar = Cellar.objects.create(
            name="Test Cellar",
            capacity=1000,
            location="Test Location",
            created_by=self.user
        )
        self.tank = Tank.objects.create(
            cellar=self.cellar,
            name="Test Tank",
            tank_type='stainless_steel',
            capacity=100,
            current_volume=0,
            created_by=self.user
        )

    def test_cellar_capacity_validation(self):
        """Test that cellar capacity cannot be reduced below total tank capacity"""
        url = reverse('cellars:edit_cellar', args=[self.cellar.id])
        response = self.client.post(url, {
            'name': 'Test Cellar',
            'capacity': 50,  # Less than tank capacity
            'location': 'Test Location'
        })
        self.assertEqual(response.status_code, 400)
        self.cellar.refresh_from_db()
        self.assertEqual(self.cellar.capacity, 1000)

    def test_tank_capacity_validation(self):
        """Test that tank capacity cannot be reduced below current volume"""
        self.tank.current_volume = 50
        self.tank.save()
        
        url = reverse('cellars:edit_tank', args=[self.tank.id])
        response = self.client.post(url, {
            'name': 'Test Tank',
            'capacity': 40,  # Less than current volume
            'current_volume': 50,
            'cellar': self.cellar.id,
            'tank_type': 'stainless_steel',
            'notes': ''
        })
        self.assertEqual(response.status_code, 400)
        self.tank.refresh_from_db()
        self.assertEqual(self.tank.capacity, 100)

    def test_resource_not_found(self):
        """Test handling of non-existent resources"""
        url = reverse('cellars:cellar_detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_tank_transfer_validation(self):
        """Test tank transfer validation logic"""
        source_tank = Tank.objects.create(
            cellar=self.cellar,
            name="Source Tank",
            tank_type='stainless_steel',
            capacity=100,
            current_volume=50,
            created_by=self.user
        )
        dest_tank = Tank.objects.create(
            cellar=self.cellar,
            name="Destination Tank",
            tank_type='stainless_steel',
            capacity=100,
            current_volume=0,
            created_by=self.user
        )
        
        url = reverse('cellars:transfer_wine')
        # Try to transfer more than available
        response = self.client.post(url, {
            'source_tank': source_tank.id,
            'destination_tank': dest_tank.id,
            'volume': 60,
            'transfer_date': '2025-02-01'
        })
        self.assertEqual(response.status_code, 400)
        
        # Valid transfer
        response = self.client.post(url, {
            'source_tank': source_tank.id,
            'destination_tank': dest_tank.id,
            'volume': 30,
            'transfer_date': '2025-02-01'
        })
        self.assertEqual(response.status_code, 302)  # Changed from 200 to 302
        source_tank.refresh_from_db()
        dest_tank.refresh_from_db()
        self.assertEqual(source_tank.current_volume, 20)
        self.assertEqual(dest_tank.current_volume, 30)

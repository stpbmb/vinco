from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Harvest, HarvestAllocation
from vineyards.models import Vineyard
from cellars.models import Cellar, Tank

class HarvestTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        
        self.vineyard = Vineyard.objects.create(
            name="Test Vineyard",
            location="Test Location",
            ownership_type="owned",
            size=1.0,
            grape_variety="merlot",
            created_by=self.user
        )
        
        self.harvest = Harvest.objects.create(
            vineyard=self.vineyard,
            date="2025-02-01",
            quantity=1000,
            juice_yield=0.75,
            created_by=self.user
        )

        self.cellar = Cellar.objects.create(
            name="Test Cellar",
            location="Test Location",
            capacity=2000,
            created_by=self.user
        )
        
        self.tank = Tank.objects.create(
            name="Test Tank",
            cellar=self.cellar,
            tank_type="stainless_steel",
            capacity=500,
            current_volume=0,
            created_by=self.user
        )

    def test_harvest_quantity_validation(self):
        """Test that harvest quantity cannot be reduced below allocated amount"""
        allocation = HarvestAllocation.objects.create(
            harvest=self.harvest,
            tank=self.tank,
            allocated_volume=300,  # Less than available juice (750L)
            allocation_date="2025-02-01",
            created_by=self.user
        )
        
        url = reverse('harvests:harvest_update', args=[self.harvest.id])
        response = self.client.post(url, {
            'vineyard': self.vineyard.id,
            'date': '2025-02-01',
            'quantity': 200,  # Try to reduce below allocated amount
            'juice_yield': 0.75
        })
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('quantity', response_data['errors'])

    def test_juice_allocation_validation(self):
        """Test juice allocation validation logic"""
        url = reverse('harvests:allocation_create')
        response = self.client.post(url, {
            'harvest': self.harvest.id,
            'tank': self.tank.id,
            'allocated_volume': 800,  # More than available juice (750L)
            'allocation_date': '2025-02-01'
        })
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('allocated_volume', response_data['errors'])

    def test_multiple_allocations(self):
        """Test multiple allocations from same harvest"""
        tank2 = Tank.objects.create(
            name="Test Tank 2",
            cellar=self.cellar,
            tank_type="stainless_steel",
            capacity=1000,
            current_volume=0,
            created_by=self.user
        )
        
        # Create first allocation (300L)
        allocation1 = HarvestAllocation.objects.create(
            harvest=self.harvest,
            tank=self.tank,
            allocated_volume=300,
            allocation_date="2025-02-01",
            created_by=self.user
        )
        
        # Try to create second allocation that would exceed available juice
        url = reverse('harvests:allocation_create')
        response = self.client.post(url, {
            'harvest': self.harvest.id,
            'tank': tank2.id,
            'allocated_volume': 500,  # Would exceed available juice (750L - 300L = 450L)
            'allocation_date': '2025-02-01'
        })
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('allocated_volume', response_data['errors'])

    def test_resource_not_found(self):
        """Test handling of non-existent resources"""
        url = reverse('harvests:harvest_update', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

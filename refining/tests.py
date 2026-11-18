from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import CrudeOil, Product, ProcessUnit, ProductionBatch, Refinery


class RefiningTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('tester', password='testpass123')
        cls.refinery = Refinery.objects.create(
            name='Тестовый НПЗ', location='г. Тестовск', capacity=10, founded=2000
        )
        cls.crude = CrudeOil.objects.create(
            name='Test Oil', density=850, sulfur=1.2, api_gravity=33
        )
        cls.unit = ProcessUnit.objects.create(
            refinery=cls.refinery, name='АВТ-1', process_type='CDU', capacity=1000
        )
        cls.product = Product.objects.create(name='Бензин АИ-92', category='FUEL')

    def test_public_pages_available(self):
        for name in ('home', 'refinery_list', 'crudeoil_list', 'unit_list',
                     'product_list', 'batch_list', 'login', 'register'):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(f'refining:{name}')).status_code, 200)

    def test_create_requires_login(self):
        response = self.client.get(reverse('refining:batch_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_authenticated_can_create_batch(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('refining:batch_create'), {
            'refinery': self.refinery.pk,
            'crude_oil': self.crude.pk,
            'unit': self.unit.pk,
            'product': self.product.pk,
            'input_volume': '1000.00',
            'output_volume': '420.00',
            'produced_at': '2026-11-17',
            'notes': '',
        })
        self.assertEqual(response.status_code, 302)
        batch = ProductionBatch.objects.get()
        self.assertEqual(batch.yield_percent, 42.0)
        self.assertEqual(batch.created_by, self.user)

    def test_form_rejects_output_greater_than_input(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('refining:batch_create'), {
            'refinery': self.refinery.pk,
            'crude_oil': self.crude.pk,
            'unit': self.unit.pk,
            'product': self.product.pk,
            'input_volume': '100.00',
            'output_volume': '200.00',
            'produced_at': '2026-11-17',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductionBatch.objects.count(), 0)
        self.assertIn('не может превышать', response.content.decode())

    def test_crude_quality_class(self):
        self.assertEqual(self.crude.quality_class, 'сернистая')
        self.crude.sulfur = 0.3
        self.assertEqual(self.crude.quality_class, 'малосернистая')

"""Заполнение базы демонстрационными данными: py manage.py seed"""
import random
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from refining.models import CrudeOil, Product, ProcessUnit, ProductionBatch, Refinery


class Command(BaseCommand):
    help = 'Заполняет БУ демонстрационными данными по нефтепереработке'

    @transaction.atomic
    def handle(self, *args, **options):
        # Чистим только демонстрационные данные приложения
        ProductionBatch.objects.all().delete()
        ProcessUnit.objects.all().delete()
        Refinery.objects.all().delete()
        CrudeOil.objects.all().delete()
        Product.objects.all().delete()

        user, _ = User.objects.get_or_create(username='demo', defaults={
            'email': 'demo@refinery.ru', 'first_name': 'Демо', 'last_name': 'Пользователь'
        })
        user.set_password('demo12345')
        user.save()

        refineries = Refinery.objects.bulk_create([
            Refinery(name='ЛУКОЙЛ — Нижегороднефтеоргсинтез', location='г. Нижний Новгород',
                     capacity=17.0, founded=1958,
                     description='Крупнейшее нефтеперерабатывающее предприятие Поволжья. Глубина переработки свыше 70%.'),
            Refinery(name='ПАО «Рязанская НПК»', location='г. Рязань',
                     capacity=13.0, founded=1960,
                     description='Современный комплекс по выпуску моторных топлив и нефтехимической продукции.'),
            Refinery(name='АО «Самарский НПЗ»', location='г. Самара',
                     capacity=8.5, founded=1945,
                     description='Предприятие полного цикла с развитой инфраструктурой переработки тяжёлого сырья.'),
        ])

        crudes = CrudeOil.objects.bulk_create([
            CrudeOil(name='Urals', density=860.0, sulfur=1.80, api_gravity=30.0,
                     description='Основная экспортная марка российской нефти, средняя по сернистости.'),
            CrudeOil(name='ESPO', density=830.0, sulfur=0.60, api_gravity=37.0,
                     description='Лёгкая малосернистая нефть восточносибирского происхождения.'),
            CrudeOil(name='Brent', density=825.0, sulfur=0.45, api_gravity=38.0,
                     description='Эталонная лёгкая нефть, используется как бенчмарк на мировых рынках.'),
            CrudeOil(name='Западносибирская', density=850.0, sulfur=1.35, api_gravity=32.5,
                     description='Нефть месторождений Западной Сибири, сернистая.'),
        ])

        products = Product.objects.bulk_create([
            Product(name='Бензин АИ-92', category='FUEL', density=745.0,
                    description='Автомобильный бензин с октановым числом 92.'),
            Product(name='Бензин АИ-95', category='FUEL', density=750.0,
                    description='Высокооктановый автомобильный бензин.'),
            Product(name='Дизельное топливо Л-0,2-40', category='DIESEL', density=840.0,
                    description='Дизельное топливо с содержанием серы не более 0,2%.'),
            Product(name='Керосин авиационный ТС-1', category='JET', density=800.0,
                    description='Топливо для турбореактивных двигателей.'),
            Product(name='Мазут М-100', category='FUEL_OIL', density=960.0,
                    description='Тяжёлое топочное мазутное топливо для котельных.'),
            Product(name='Масло моторное 5W-30', category='LUBE', density=870.0,
                    description='Синтетическое моторное масло для современных двигателей.'),
            Product(name='Битум БНД 60/90', category='BITUMEN', density=1000.0,
                    description='Дорожный вяжущий битум.'),
            Product(name='Пропан-бутан (СУГ)', category='GAS', density=530.0,
                    description='Сжиженный углеводородный газ для бытовых и промышленных нужд.'),
            Product(name='Бензол', category='PETROCHEM', density=880.0,
                    description='Ароматический углеводород — сырьё для нефтехимии.'),
        ])

        units = []
        configs = [
            ('АВТ-1', 'CDU', 6000, 1962), ('АВТ-2', 'CDU', 5000, 1975),
            ('ВТ-1', 'VDU', 3000, 1978), ('ККФ', 'FCC', 2200, 1985),
            ('Гидроочистка дизеля', 'HYDRO', 2800, 2001),
            ('Риформинг Л-35', 'REFORM', 1200, 1990),
            ('Установка коксования', 'COKING', 900, 2010),
            ('Изомеризация', 'ISOM', 700, 2015),
        ]
        for refinery in refineries:
            for name, ptype, cap, year in configs:
                units.append(ProcessUnit(
                    refinery=refinery, name=name, process_type=ptype,
                    capacity=cap, commissioned=year,
                ))
        ProcessUnit.objects.bulk_create(units)

        units_by_refinery = {}
        for u in ProcessUnit.objects.all():
            units_by_refinery.setdefault(u.refinery_id, []).append(u)

        random.seed(42)
        batches = []
        today = date.today()
        product_ids = list(Product.objects.values_list('id', flat=True))
        for i in range(40):
            refinery = random.choice(refineries)
            crude = random.choice(crudes)
            unit = random.choice(units_by_refinery[refinery.id])
            product = Product.objects.get(id=random.choice(product_ids))
            input_volume = round(random.uniform(500, 5000), 2)
            base_yield = {'CDU': 0.42, 'VDU': 0.30, 'FCC': 0.40, 'HYDRO': 0.88,
                          'REFORM': 0.70, 'COKING': 0.52, 'ISOM': 0.84}[unit.process_type]
            output_volume = round(input_volume * base_yield * random.uniform(0.92, 1.04), 2)
            batches.append(ProductionBatch(
                refinery=refinery, crude_oil=crude, unit=unit, product=product,
                input_volume=input_volume, output_volume=output_volume,
                produced_at=today - timedelta(days=random.randint(0, 120)),
                created_by=user,
                notes='Демонстрационная партия.' if i % 5 == 0 else '',
            ))
        ProductionBatch.objects.bulk_create(batches)

        self.stdout.write(self.style.SUCCESS(
            'Готово: 3 НПЗ, 4 марки нефти, 24 установки, 9 продуктов, 40 партий.\n'
            'Демо-пользователь: demo / demo12345'
        ))

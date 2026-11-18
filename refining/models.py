from django.conf import settings
from django.db import models
from django.urls import reverse


class Refinery(models.Model):
    """Нефтеперерабатывающий завод (НПЗ)."""

    name = models.CharField('Название', max_length=150, unique=True)
    location = models.CharField('Местоположение', max_length=150)
    capacity = models.PositiveIntegerField(
        'Мощность, млн тонн/год', help_text='Проектная мощность по переработке сырой нефти'
    )
    founded = models.PositiveSmallIntegerField('Год пуска', null=True, blank=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'НПЗ'
        verbose_name_plural = 'Нефтеперерабатывающие заводы'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('refining:refinery_detail', args=[self.pk])


class CrudeOil(models.Model):
    """Марка сырой нефти (сырьё)."""

    name = models.CharField('Марка нефти', max_length=100, unique=True)
    density = models.DecimalField('Плотность, кг/м³', max_digits=7, decimal_places=1)
    sulfur = models.DecimalField('Содержание серы, %', max_digits=4, decimal_places=2)
    api_gravity = models.DecimalField('API-плотность', max_digits=5, decimal_places=1, blank=True, null=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Марка нефти'
        verbose_name_plural = 'Марки сырой нефти'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def quality_class(self):
        """Класс нефти по сернистости."""
        if self.sulfur <= 0.5:
            return 'малосернистая'
        if self.sulfur <= 1.5:
            return 'сернистая'
        return 'высокосернистая'


class ProcessUnit(models.Model):
    """Технологическая установка НПЗ."""

    PROCESS_TYPES = [
        ('CDU', 'Атмосферная перегонка (АВТ)'),
        ('VDU', 'Вакуумная перегонка'),
        ('FCC', 'Каталитический крекинг'),
        ('HYDRO', 'Гидроочистка'),
        ('REFORM', 'Каталитический риформинг'),
        ('COKING', 'Коксование'),
        ('ISOM', 'Изомеризация'),
    ]

    refinery = models.ForeignKey(
        Refinery, on_delete=models.CASCADE, related_name='units', verbose_name='НПЗ'
    )
    name = models.CharField('Название установки', max_length=150)
    process_type = models.CharField('Тип процесса', max_length=10, choices=PROCESS_TYPES)
    capacity = models.PositiveIntegerField('Мощность, тыс. тонн/год')
    commissioned = models.PositiveSmallIntegerField('Год ввода', null=True, blank=True)

    class Meta:
        verbose_name = 'Установка'
        verbose_name_plural = 'Технологические установки'
        ordering = ['refinery', 'name']

    def __str__(self):
        return f'{self.name} ({self.refinery.name})'

    def get_process_type_display_name(self):
        return dict(self.PROCESS_TYPES).get(self.process_type, self.process_type)


class Product(models.Model):
    """Нефтепродукт."""

    CATEGORY_CHOICES = [
        ('FUEL', 'Моторное топливо'),
        ('DIESEL', 'Дизельное топливо'),
        ('JET', 'Авиационный керосин'),
        ('FUEL_OIL', 'Топочный мазут'),
        ('LUBE', 'Смазочные материалы'),
        ('BITUMEN', 'Битум'),
        ('PETROCHEM', 'Нефтехимия'),
        ('GAS', 'Сжиженные газы'),
    ]

    name = models.CharField('Название продукта', max_length=150, unique=True)
    category = models.CharField('Категория', max_length=12, choices=CATEGORY_CHOICES)
    density = models.DecimalField(
        'Плотность, кг/м³', max_digits=7, decimal_places=1, blank=True, null=True
    )
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Нефтепродукт'
        verbose_name_plural = 'Нефтепродукты'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductionBatch(models.Model):
    """Партия переработки: учёт сырья, процесса и выхода продукта."""

    refinery = models.ForeignKey(
        Refinery, on_delete=models.CASCADE, related_name='batches', verbose_name='НПЗ'
    )
    crude_oil = models.ForeignKey(
        CrudeOil, on_delete=models.PROTECT, related_name='batches', verbose_name='Марка нефти'
    )
    unit = models.ForeignKey(
        ProcessUnit, on_delete=models.PROTECT, related_name='batches', verbose_name='Установка'
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='batches', verbose_name='Продукт'
    )
    input_volume = models.DecimalField(
        'Объём сырья, тонн', max_digits=12, decimal_places=2
    )
    output_volume = models.DecimalField(
        'Объём продукта, тонн', max_digits=12, decimal_places=2
    )
    produced_at = models.DateField('Дата переработки')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='batches',
        verbose_name='Добавил',
    )
    notes = models.TextField('Примечание', blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Партия переработки'
        verbose_name_plural = 'Партии переработки'
        ordering = ['-produced_at', '-created_at']

    def __str__(self):
        return f'{self.product.name} — {self.input_volume} т ({self.produced_at})'

    def get_absolute_url(self):
        return reverse('refining:batch_detail', args=[self.pk])

    @property
    def yield_percent(self):
        """Процент выхода продукта из сырья."""
        if self.input_volume and self.input_volume > 0:
            return round(float(self.output_volume) / float(self.input_volume) * 100, 2)
        return 0

from django.contrib import admin

from .models import CrudeOil, Product, ProcessUnit, ProductionBatch, Refinery


@admin.register(Refinery)
class RefineryAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'founded')
    search_fields = ('name', 'location')
    list_filter = ('founded',)


@admin.register(CrudeOil)
class CrudeOilAdmin(admin.ModelAdmin):
    list_display = ('name', 'density', 'sulfur', 'api_gravity', 'quality_class')
    search_fields = ('name',)


@admin.register(ProcessUnit)
class ProcessUnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'refinery', 'process_type', 'capacity', 'commissioned')
    list_filter = ('process_type', 'refinery')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'density')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(ProductionBatch)
class ProductionBatchAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'refinery', 'crude_oil', 'unit',
        'input_volume', 'output_volume', 'yield_percent', 'produced_at',
    )
    list_filter = ('refinery', 'product', 'produced_at')
    search_fields = ('product__name', 'notes')
    date_hierarchy = 'produced_at'
    autocomplete_fields = ('refinery', 'crude_oil', 'unit', 'product')

    def yield_percent(self, obj):
        return f'{obj.yield_percent}%'
    yield_percent.short_description = 'Выход, %'

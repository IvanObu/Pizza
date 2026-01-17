from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Drink, Category, RomaPizza, Toppings, Pizza, Combo, ComboDrink, ComboPizza, ComboRomaPizza
# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)} 

@admin.register(Drink)
class DrinkAdmin(admin.ModelAdmin):
    list_display = ["name", 'slug', 'price', 'image', 'new']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Toppings)
class ToppingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active', 'top_category']

@admin.register(RomaPizza)
class RomaPizzaAdmin(admin.ModelAdmin):
    list_display = ["name", 'slug', 'price', 'image', 'weight', 'category','new']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['toppings']
    list_filter = ['category', 'new']
    search_fields = ['name']


@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_price_s', 'is_active', 'new', 'auto_calculate']
    list_filter = ['category', 'is_active', 'new', 'auto_calculate']
    filter_horizontal = ['composition']
    list_editable = ['is_active', 'new', 'auto_calculate']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    # Поля в админке
    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'slug', 'image', 'category', 'is_active', 'new']
        }),
        ('Состав', {
            'fields': ['composition']
        }),
        ('Базовые параметры (размер S - 25см)', {
            'fields': ['base_price_s', 'base_weight_s'],
            'description': 'Цена и вес для маленькой пиццы (25 см)'
        }),
        ('Настройки расчета', {
            'fields': ['auto_calculate'],
            'description': 'Включите для автоматического расчета цен и веса'
        }),
        ('Коэффициенты для размера M (30см)', {
            'fields': [('price_multiplier_m', 'weight_multiplier_m')],
            'classes': ['collapse'],
            'description': 'Коэффициенты для цены и веса среднего размера'
        }),
        ('Коэффициенты для размера L (35см)', {
            'fields': [('price_multiplier_l', 'weight_multiplier_l')],
            'classes': ['collapse'],
            'description': 'Коэффициенты для цены и веса большого размера'
        }),
        ('Коэффициенты для размера XL (40см)', {
            'fields': [('price_multiplier_xl', 'weight_multiplier_xl')],
            'classes': ['collapse'],
            'description': 'Коэффициенты для цены и веса очень большого размера'
        }),
    ]

class ComboDrinkInline(admin.TabularInline):
    model = ComboDrink
    extra = 0  
    min_num = 0  

class ComboPizzaInline(admin.TabularInline):
    model = ComboPizza
    extra = 0  
    min_num = 0  
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "pizza":
            kwargs["queryset"] = Pizza.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ComboRomaPizzaInline(admin.TabularInline):
    model = ComboRomaPizza
    extra = 0  
    min_num = 0  

@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [ComboPizzaInline, ComboRomaPizzaInline, ComboDrinkInline]
    prepopulated_fields = {'slug': ('name',)}

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)



    
from django.contrib import admin
from django.utils.html import format_html
from .models import Drink, DrinkSize, Category, RomaPizza, Toppings, Pizza, Combo, ComboDrink, ComboPizza, ComboRomaPizza, ActionImage, ActionGallery
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)} 

class DrinkSizeInline(admin.TabularInline):
    model = DrinkSize
    extra = 0
    min_num = 1

@admin.register(Drink)
class DrinkAdmin(admin.ModelAdmin):
    list_display = ["name", "new"]
    prepopulated_fields = {'slug': ('name',)}
    inlines = [DrinkSizeInline]

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
    filter_horizontal = ['toppings']
    list_editable = ['is_active', 'new', 'auto_calculate']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'slug', 'image', 'category', 'is_active', 'new']
        }),
        ('Состав', {
            'fields': ['toppings']
        }),
        ('Базовые параметры (размер S - 25см)', {
            'fields': ['base_price_s', 'base_weight_s'],
            'description': 'Цена и вес для маленькой пиццы (25 см)'
        }),
        ('Настройки расчета', {
            'fields': ['auto_calculate'],
            'description': 'Включите для автоматического расчета цен и веса'
        }),
        ('Коэффициенты размеров (авторасчёт)', {
            'fields': [
                ('price_multiplier_m', 'weight_multiplier_m'),
                ('price_multiplier_l', 'weight_multiplier_l'),
                ('price_multiplier_xl', 'weight_multiplier_xl'),
            ],
            'classes': ['coef-fields'],
            'description': 'Используются при включённом авторасчёте'
        }),
        ('Ручные значения для размеров M / L / XL', {
            'fields': [
                ('price_m', 'weight_m'),
                ('price_l', 'weight_l'),
                ('price_xl', 'weight_xl'),
            ],
            'classes': ['manual-fields'],
        }),
    ]

    class Media:
        js = ('admin/js/pizza_admin.js',)
        css = {'all': ('admin/css/pizza_admin.css',)}

class ComboDrinkInline(admin.TabularInline):
    model = ComboDrink
    extra = 0  
    min_num = 0  

class ComboPizzaInline(admin.TabularInline):
    model = ComboPizza
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class Form(formset.form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                if self.instance.pk and self.instance.pizza:
                    price = self.instance.pizza.get_price_for_size(self.instance.size)
                    self.fields['pizza'].widget.attrs['data-price'] = price

        formset.form = Form
        return formset


class ComboRomaPizzaInline(admin.TabularInline):
    model = ComboRomaPizza
    extra = 0  
    min_num = 0  

@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ['name', 'items_price', 'final_price']
    inlines = [ComboPizzaInline, ComboRomaPizzaInline, ComboDrinkInline]
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['auto_price_preview']

    fieldsets = (
        ('Основное', {
            'fields': ('name', 'slug', 'category')
        }),
        ('Цена', {
            'fields': ('price', 'auto_price_preview'),
            'description': 'Если цена не задана — используется автоматический расчёт'
        }),
    )

    def auto_price_preview(self, obj):
        if not obj.pk:
            return "Будет рассчитана автоматически"
        return obj.get_items_price()

    auto_price_preview.short_description = "Автоматическая цена"


    class Media:
        js = ('admin/js/combo_admin.js',)

    def items_price(self, obj):
        return obj.get_items_price()
    items_price.short_description = "Цена позиций без скидок"

    def final_price(self, obj):
        return obj.get_final_price()
    final_price.short_description = "Итоговая цена"


class ActionImageInline(admin.TabularInline):
    model = ActionImage
    extra = 1
    fields = ['image','preview']
    readonly_fields = ['preview']
    
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="100" />', obj.image.url)
        return "—"
    preview.short_description = "Превью"

@admin.register(ActionGallery)
class ActionGalleryAdmin(admin.ModelAdmin):
    inlines = [ActionImageInline]
    list_display = ['title', 'image_count']
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = "Кол-во изображений"
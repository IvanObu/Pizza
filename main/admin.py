from django.contrib import admin
from django.utils.html import format_html
from .models import Drink, Category, RomaPizza, SizeTemplate, Toppings, PizzaSize, Pizza
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

class PizzaSizeInline(admin.TabularInline):
    model = PizzaSize
    extra = 0  # Не показывать пустые строки
    min_num = 1  # Минимум 1 размер в шаблоне
    ordering = ['order']
    def prices_display(self, obj):
        if not obj.pk:  
            return "Сначала сохраните"
        
        sizes = obj.get_all_sizes_with_prices()
        if not sizes:
            return "Нет размеров"
        
        # Создаем красивый список цен
        price_list = []
        for size in sizes:
            price_list.append(f"{size['size']}: {size['price']} руб")
        
        return format_html("<br>".join(price_list))
    prices_display.short_description = "Цены по размерам"
    
    # Показываем изображение
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url
            )
        return "Нет фото"
    image_preview.short_description = "Изображение"

@admin.register(SizeTemplate)
class SizeTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'sizes_count', 'sizes_list']
    list_editable = ['is_default']  
    inlines = [PizzaSizeInline]  
    
    def sizes_count(self, obj):
        return obj.sizes.count()
    sizes_count.short_description = "Кол-во размеров"
    
    def sizes_list(self, obj):
        sizes = obj.sizes.all().order_by('order')
        return ", ".join([f"{s.get_size_display()} (x{s.multiplier})" for s in sizes])
    sizes_list.short_description = "Размеры в шаблоне"


@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ["name", 'slug', 'base_price', 'image', 'weight', 'category', 'size_template','new']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['toppings']
    list_filter = ['category', 'new']
    search_fields = ['name']



# class ToppingAdmin(admin.ModelAdmin):
#     list_display = ['name', 'category', 'price']
#     list_filter = ['category']
#     search_fields = ['name']

# class ProductSizeInline(admin.TabularInline):
#     model = ProductSize
#     extra = 1
#     fields = ['size', 'stock']
#     autocomplete_fields = ['size']   

# class ProductAdmin(admin.ModelAdmin):
#     list_display = ['name', 'category', 'price', 'description', 'image', 'weight']
#     list_filter = ['category', 'price','weight']
#     search_fields = ['category', 'price', 'description', 'weight']
#     prepopulated_fields = {'slug': ('name',)} 
#     inlines = [ProductSizeInline]


# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ['name', 'has_sizes', 'has_toppings', 'size_type']
#     prepopulated_fields = {'slug': ('name',)} 

# class SizeAdmin(admin.ModelAdmin):
#     list_display = ['name']
#     list_filter = ['unit']
#     search_fields = ['name']

# admin.site.register(Topping, ToppingAdmin)
# admin.site.register(Product, ProductAdmin)
# admin.site.register(Size, SizeAdmin)
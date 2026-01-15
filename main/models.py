from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=40, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Toppings(models.Model):
    class TopCategory(models.TextChoices):
        SAUCE = 'SC', 'Соус'
        MEAT = 'MT', 'Мясо'
        VEGETABLES = 'VG', 'Овощи/Фрукты'
        CHEESE = 'CH', 'Сыр'
        SPICES = 'SP', 'Специи/Зелень'
        SEAFOOD = 'SF', 'Морепродукты'

    name = models.CharField(max_length=25, unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=8, default=50.00, verbose_name="Цена",
        help_text="Цена в рублях")
    is_active = models.BooleanField(default=True)
    top_category = models.CharField(choices=TopCategory.choices, max_length=2, verbose_name="категория топпинга")
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок сортировки"
    )
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Топпинг"
        verbose_name_plural = "Топпинги"

    def __str__(self):
        return f"{self.name} (+{self.price} руб)"


class Drink(models.Model):
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=40, unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    image = models.ImageField(upload_to="Drinks/%Y/%m/%d")
    new = models.BooleanField(default=False)
    # size = подумать, мб это в ордер засунуть
    class Meta:
        ordering = ['name']
        verbose_name = "Напиток"
        verbose_name_plural = "Напитки"


class RomaPizza(models.Model):
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=40, unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    image = models.ImageField(upload_to="RomaPizza/%Y/%m/%d")
    weight = models.PositiveIntegerField(default=400)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    new = models.BooleanField(default=False)
    toppings = models.ManyToManyField(Toppings)

class SizeTemplate(models.Model):

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Название шаблона",
        help_text="Например: Стандартные размеры пицц"
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name="Шаблон по умолчанию",
        help_text="Использовать этот шаблон для новых пицц"
    )
    
    class Meta:
        verbose_name = "Шаблон размеров"
        verbose_name_plural = "Шаблоны размеров"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Только один шаблон по умолчанию в моменте
        if self.is_default:
            SizeTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class PizzaSize(models.Model):

    SIZE_CHOICES = [
        ('S', 'Маленькая (25 см)'),
        ('M', 'Средняя (30 см)'),
        ('L', 'Большая (35 см)'),
        ('XL', 'Очень большая (40 см)'),
    ]
    
    template = models.ForeignKey(
        SizeTemplate,
        on_delete=models.CASCADE,
        related_name='sizes',
        verbose_name="Шаблон"
    )
    size = models.CharField(
        max_length=2,
        choices=SIZE_CHOICES,
        verbose_name="Размер"
    )
    diameter_cm = models.PositiveIntegerField(
        verbose_name="Диаметр (см)",
    )
    multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.00,
        verbose_name="Коэффициент цены",
        help_text="Множитель для базовой цены. Пример: 1.3 = +30%"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок"
    )
    
    class Meta:
        ordering = ['template', 'order']
        unique_together = ['template', 'size'] # узнать
        verbose_name = "Размер пиццы"
        verbose_name_plural = "Размеры пицц"
    
    def __str__(self):
        return f"{self.template.name} - {self.get_size_display()}"

class Pizza(models.Model):
    name = models.CharField(
        max_length=30, 
        unique=True,
        verbose_name="Название"
    )
    slug = models.SlugField(
        max_length=40, 
        unique=True,
        verbose_name="Slug"
    )
    
    base_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Базовая цена",
        help_text="Цена для самого маленького размера (S)",
        validators=[MinValueValidator(0)] # Проверка что цена положительная
    )
    
    image = models.ImageField(
        upload_to="Pizza/%Y/%m/%d",
        blank=True,
        null=True,
        verbose_name="Изображение"
    )
    weight = models.PositiveIntegerField(
        default=400,
        verbose_name="Вес (г)",
        help_text="Вес пиццы размера S в граммах"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='pizzas',
        verbose_name="Категория"
    )
    
    size_template = models.ForeignKey(
        SizeTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Шаблон размеров",
        help_text="Если не выбран, используется шаблон по умолчанию"
    )
    
    new = models.BooleanField(
        default=False,
        verbose_name="Новинка"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна"
    )
    
    toppings = models.ManyToManyField(
        Toppings,
        blank=True,
        verbose_name="Доступные топпинги",
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = "Пицца"
        verbose_name_plural = "Пиццы"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    # МЕТОДЫ ДЛЯ РАБОТЫ С РАЗМЕРАМИ
    
    @property
    def active_size_template(self):
        """Получить активный шаблон размеров"""
        if self.size_template:
            return self.size_template
        default_template = SizeTemplate.objects.filter(is_default=True).first()
        if default_template:
            return default_template
        return SizeTemplate.objects.first()
    
    def get_price_for_size(self, size_code):
        try:
            size = self.active_size_template.sizes.get(size=size_code)
            return round(self.base_price * size.multiplier, 2)
        except (SizeTemplate.DoesNotExist, PizzaSize.DoesNotExist):
            return self.base_price
    
    def get_all_sizes_with_prices(self):
        result = []
        if self.active_size_template:
            for size_obj in self.active_size_template.sizes.all().order_by('order'):
                price = round(self.base_price * size_obj.multiplier, 2)
                result.append({
                    'size': size_obj.size,
                    'size_display': size_obj.get_size_display(),
                    'diameter_cm': size_obj.diameter_cm,
                    'multiplier': float(size_obj.multiplier),
                    'price': price,
                    'weight_g': self.weight 
                })
        return result


# class Combo(models.Model):
#     name = models.CharField(max_length=30, unique=True)
#     slug = models.SlugField(max_length=40, unique=True)
#     pizzas = models.ForeignKey(Pizza, null=True, blank=True)
#     roma_pizzas = models.ForeignKey(RomaPizza, null=True, blank=True)
#     drinks = models.ForeignKey(Drink, null=True, blank=True)
#     class Meta:
#         ordering = ['name']
#         verbose_name = "Комбо набор"
#         verbose_name_plural = "Комбо наборы"

#     def __str__(self):
#         return self.name
    
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         super().save(*args, **kwargs)
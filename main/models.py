from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
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
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='drinks',
    )
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=40, unique=True)
    image = models.ImageField(upload_to="Drinks/%Y/%m/%d")
    new = models.BooleanField(default=False)
    description = models.TextField(max_length=250)

    class Meta:
        ordering = ['name']
        verbose_name = "Напиток"
        verbose_name_plural = "Напитки"

    def __str__(self):
        return self.name


class DrinkSize(models.Model):
    class Size(models.TextChoices):
        S = 'S', 'Маленький (250 мл)'
        M = 'M', 'Средний (340 мл)'
        L = 'L', 'Большой (420 мл)'

    drink = models.ForeignKey(
        Drink,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    size = models.CharField(
        max_length=1,
        choices=Size.choices
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    VOLUME_MAP = {
        'S': 250,
        'M': 340,
        'L': 420,
    }

    @property
    def volume_ml(self):
        return self.VOLUME_MAP[self.size]

    class Meta:
        unique_together = ['drink', 'size']



    def __str__(self):
        return f"{self.drink.name} — {self.volume_ml}"
    

class RomaPizza(models.Model):
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=40, unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    image = models.ImageField(upload_to="RomaPizza/%Y/%m/%d")
    weight = models.PositiveIntegerField(default=400)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    new = models.BooleanField(default=False)
    toppings = models.ManyToManyField(Toppings)

class Pizza(models.Model):
    SIZE_CHOICES = [
        ('S', 'Маленькая (25 см)'),
        ('M', 'Средняя (30 см)'),
        ('L', 'Большая (35 см)'),
        ('XL', 'Очень большая (40 см)'),
    ]
    
    name = models.CharField(max_length=30, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=40, unique=True, verbose_name="Slug")
    image = models.ImageField(upload_to="Pizza/%Y/%m/%d", blank=True, null=True, verbose_name="Изображение")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='pizzas', verbose_name="Категория")
    new = models.BooleanField(default=False, verbose_name="Новинка")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    composition = models.ManyToManyField(Toppings, blank=True, verbose_name="Ингредиенты")
    
    # Базовые параметры для размера S (это будут значения по умолчанию)
    base_price_s = models.PositiveIntegerField(
        default=400,
        verbose_name="Базовая цена (S)",
        help_text="Цена для маленького размера (25 см)",
        validators=[MinValueValidator(0)]
    )
    base_weight_s = models.PositiveIntegerField(
        default=400,
        verbose_name="Базовый вес (S)",
        help_text="Вес для маленького размера в граммах"
    )
    
    # Настройки автоматического расчета
    auto_calculate = models.BooleanField(
        default=True,
        verbose_name="Авторасчет",
        help_text="Автоматически рассчитывать параметры для других размеров"
    )
    
    # Коэффициенты для авторасчета
    price_multiplier_m = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.3,
        verbose_name="Коэф. цены M",
    )
    price_multiplier_l = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.6,
        verbose_name="Коэф. цены L",
    )
    price_multiplier_xl = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=2.0,
        verbose_name="Коэф. цены XL",
        
    )
    
    weight_multiplier_m = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.3,
        verbose_name="Коэф. веса M"
    )
    weight_multiplier_l = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.6,
        verbose_name="Коэф. веса L"
    )
    weight_multiplier_xl = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=2.0,
        verbose_name="Коэф. веса XL"
    )

    # Ручные цены и веса
    price_m = models.PositiveIntegerField(null=True, blank=True, verbose_name="Цена M")
    price_l = models.PositiveIntegerField(null=True, blank=True, verbose_name="Цена L")
    price_xl = models.PositiveIntegerField(null=True, blank=True, verbose_name="Цена XL")

    weight_m = models.PositiveIntegerField(null=True, blank=True, verbose_name="Вес M")
    weight_l = models.PositiveIntegerField(null=True, blank=True, verbose_name="Вес L")
    weight_xl = models.PositiveIntegerField(null=True, blank=True, verbose_name="Вес XL")
    
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
    
    def get_available_sizes(self):
        """Проверка на доступный размеры"""
        sizes = ['S']
        
        if self.price_multiplier_m > 0:
            sizes.append('M')
        if self.price_multiplier_l > 0:
            sizes.append('L')
        if self.price_multiplier_xl > 0:
            sizes.append('XL')
            
        return sizes
    
    def get_price_for_size(self, size):
        """Авто подстановка или ручная подстановка в зависимости от режима"""
        if size == 'S':
            return self.base_price_s

        if self.auto_calculate:
            multipliers = {
                'M': self.price_multiplier_m,
                'L': self.price_multiplier_l,
                'XL': self.price_multiplier_xl,
            }
            return int(self.base_price_s * multipliers.get(size, 1))

        manual_prices = {
            'M': self.price_m,
            'L': self.price_l,
            'XL': self.price_xl,
        }
        return manual_prices.get(size)
    
    def get_weight_for_size(self, size):

        if size == 'S':
            return self.base_weight_s

        if self.auto_calculate:
            multipliers = {
                'M': self.weight_multiplier_m,
                'L': self.weight_multiplier_l,
                'XL': self.weight_multiplier_xl,
            }
            return int(self.base_weight_s * multipliers.get(size, 1))

        manual_weights = {
            'M': self.weight_m,
            'L': self.weight_l,
            'XL': self.weight_xl,
        }
        return manual_weights.get(size)
    
    def get_diameter_for_size(self, size):
        """Получить диаметр для конкретного размера"""
        diameters = {
            'S': 25,
            'M': 30,
            'L': 35,
            'XL': 40,
        }
        return diameters.get(size)
    
    def get_size_pizza_info(self, size):
        """Получить полную информацию о размере"""
        return {
            'size': size,
            'size_display': dict(self.SIZE_CHOICES).get(size, 'Маленькая'),
            'price': self.get_price_for_size(size),
            'weight': self.get_weight_for_size(size),
            'diameter': self.get_diameter_for_size(size),
        }
    
    def get_all_info(self):
        """Получить информацию обо всех доступных размерах"""
        result = []
        for size in self.get_available_sizes():
            result.append(self.get_size_pizza_info(size))
        return result
    
    def clean(self):
        """ Валидация при сохранении модели"""
        if not self.auto_calculate:
            required_fields = [
                self.price_m, self.price_l, self.price_xl,
                self.weight_m, self.weight_l, self.weight_xl
            ]

            if any(v is None for v in required_fields):
                raise ValidationError(
                    "При выключенном авторасчёте необходимо заполнить все цены и веса для размеров M, L, XL"
                )

    def save(self, *args, **kwargs):
        self.full_clean()  # ← ВАЖНО так как clean не вызовится
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Combo(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=40, unique=True)
    pizzas = models.ManyToManyField(Pizza, through='ComboPizza', blank=True)
    roman_pizzas = models.ManyToManyField(RomaPizza, through='ComboRomaPizza', blank=True)
    drinks = models.ManyToManyField(DrinkSize, through='ComboDrink', blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=380)
    class Meta:
        verbose_name = "Комбо набор"
        verbose_name_plural = "Комбо наборы"
        

    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Фиксированная цена (если задана)"
    )

    def get_items_price(self):
        total = 0

        for item in self.combopizza_set.select_related('pizza'):
            if item.pizza:
                total += item.pizza.get_price_for_size(item.size) * item.quantity

        for item in self.comboromapizza_set.select_related('roman_pizza'):
            total += item.roman_pizza.price * item.quantity

        for item in self.combodrink_set.select_related('drink_size', 'drink_size__drink'):
            total += item.drink_size.price * item.quantity

        return total

    def get_final_price(self):
        """ Если задана цена комбо — используем её, иначе считаем автоматически """
        return self.price if self.price else self.get_items_price()

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
class ComboPizza(models.Model):
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE)
    pizza = models.ForeignKey(Pizza, null=True, blank=True, on_delete=models.CASCADE)
    size = models.CharField(max_length=2, choices=Pizza.SIZE_CHOICES, default='M')
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        unique_together = ['combo', 'pizza', 'size']

class ComboRomaPizza(models.Model):
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE)
    roman_pizza = models.ForeignKey(RomaPizza, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    
    class Meta:
        unique_together = ['combo', 'roman_pizza']
    
    def __str__(self):
        return f"{self.roman_pizza.name} x{self.quantity}"

class ComboDrink(models.Model):
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE)
    drink_size = models.ForeignKey(DrinkSize, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    
    class Meta:
        unique_together = ['combo', 'drink_size']
    
    def __str__(self):
        return (
        f"{self.drink_size.drink.name} "
        f"({self.drink_size.get_size_display()}) × {self.quantity}"
    )
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import Http404
from django.template.response import TemplateResponse
from .models import *
from django.db.models import Q

from .mappers import map_combo, map_pizza, map_drink, map_roma_pizza

# Create your views here.


class IndexView(TemplateView):
    template_name = "main/base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context['action_gallery'] = ActionGallery.objects.first()
        print(context)
        context["current_category"] = None
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get("HX-Request"):
            return TemplateResponse(request, "main/home_content.html", context)
        return TemplateResponse(request, self.template_name, context)


class CatalogView(TemplateView):
    template_name = "main/base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category = get_object_or_404(Category, slug=kwargs["slug"])
        search = self.request.GET.get("q", "").strip()
        sort = self.request.GET.get("sort")

        products = []

        pizzas = Pizza.objects.filter(category=category, is_active=True)

        if search:
            pizzas = pizzas.filter(
                Q(name__icontains=search) |
                Q(toppings__name__icontains=search)
            ).distinct()

        if sort == "price_asc":
            pizzas = pizzas.order_by("base_price_s")
        elif sort == "price_desc":
            pizzas = pizzas.order_by("-base_price_s")

        products += [map_pizza(p) for p in pizzas]

        romas = RomaPizza.objects.filter(category=category)

        if search:
            romas = romas.filter(
                Q(name__icontains=search) |
                Q(toppings__name__icontains=search)
            ).distinct()

        if sort == "price_asc":
            romas = romas.order_by("price")
        elif sort == "price_desc":
            romas = romas.order_by("-price")

        products += [map_roma_pizza(r) for r in romas]

        drinks = DrinkSize.objects.filter(
            drink__category=category
        ).select_related("drink")

        if search:
            drinks = drinks.filter(
                Q(drink__name__icontains=search) |
                Q(drink__description__icontains=search)
            ).distinct()

        if sort == "price_asc":
            drinks = drinks.order_by("price")
        elif sort == "price_desc":
            drinks = drinks.order_by("-price")

        products += [map_drink(d) for d in drinks]
        combos = Combo.objects.filter(category=category)

        if search:
            combos = combos.filter(name__icontains=search)

        if sort == "price_asc":
            combos = combos.order_by("price")
        elif sort == "price_desc":
            combos = combos.order_by("-price")

        products += [map_combo(c) for c in combos]

        context.update({
            "categories": Category.objects.all(),
            "current_category": category,
            "products": products,
            "search": search,
            "sort": sort,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get("HX-Request"):
            return TemplateResponse(request, "main/home_content.html", context)
        return TemplateResponse(request, self.template_name, context)


class ProductDetailView(TemplateView):
    template_name = "main/product_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs["slug"]

        product = self.get_product_by_slug(slug)

        context["product"] = product
        context["categories"] = Category.objects.all()
        return context

    def get_product_by_slug(self, slug):
        pizza = Pizza.objects.filter(slug=slug, is_active=True).first()
        if pizza:
            return map_pizza(pizza)

        roma = RomaPizza.objects.filter(slug=slug).first()
        if roma:
            return map_roma_pizza(roma)

        drink = Drink.objects.filter(slug=slug).first()
        if drink:
            size = drink.variants.first()
            if not size:
                raise Http404()
            return map_drink(size)

        combo = Combo.objects.filter(slug=slug).first()
        if combo:
            return map_combo(combo)

        raise Http404()
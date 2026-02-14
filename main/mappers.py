def map_pizza(pizza):
    sizes = pizza.get_all_info()
    default = sizes[0]

    return {
        "type": "pizza",
        "id": pizza.id,
        "slug": pizza.slug,
        "name": pizza.name,
        "image": pizza.image.url if pizza.image else None,

        "price": default["price"],
        "weight": default["weight"],
        "diameter": default["diameter"],
        "current_size": default["size"],
        "sizes": sizes,

        "toppings": [t.name for t in pizza.toppings.all()],
    }


def map_roma_pizza(pizza):
    return {
        "type": "roma",
        "id": pizza.id,
        "slug": pizza.slug,
        "name": pizza.name,
        "price": pizza.price,
        "weight": pizza.weight,
        "image": pizza.image.url if pizza.image else None,
        "toppings": [t.name for t in pizza.toppings.all()],
    }


def map_drink(drink_size):
    return {
        "type": "drink",
        "id": drink_size.id,
        "slug": drink_size.drink.slug,
        "name": drink_size.drink.name,
        "price": drink_size.price,
        "volume": drink_size.volume_ml,
        "size": drink_size.size,
        "image": drink_size.drink.image.url if drink_size.drink.image else None,
    }


def map_combo(combo):
    return {
        "type": "combo",
        "id": combo.id,
        "slug": combo.slug,
        "name": combo.name,
        "price": combo.get_final_price(),
    }
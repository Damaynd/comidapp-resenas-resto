from django.shortcuts import render
from .models import *
from django.db.models import Prefetch, Q, Count
from aplicacion.models import Restaurant, Photo



# Create your views here.
# views.py

def home(request):
    restaurantes = (
        Restaurant.objects
        .prefetch_related(
            Prefetch('photos', queryset = Photo.objects.filter(category = 'other').order_by('id'), to_attr = 'cover_photos')))
    return render(request, 'home.html', {'restaurantes': restaurantes})

# Cuando haces click en un restaurante de home.html, esta funcion te llevara a detalle_restaurante.html para ver mas detalles
def detalle_restaurante(request, restaurante_id):
    restaurante = Restaurant.objects.get(pk=restaurante_id)
    return render(request, "detalle_restaurante.html", {"restaurante": restaurante})



def buscar(request):
    q = (request.GET.get("q") or "").strip()

    if not q:
        return render(request, "buscar.html", {
            "q": "",
            "restaurant_groups": [],
            "counts": {"restaurants": 0, "dishes": 0},
        })

    # filtros de restaurantes
    rs_q = (
        Q(name__icontains = q) |
        Q(address__icontains = q) |
        Q(cuisines__name__icontains = q) |
        Q(tags__name__icontains = q) |
        Q(tags__code__icontains = q)
    )

    restaurants_qs = (
        Restaurant.objects
        .filter(rs_q)
        .prefetch_related(
            Prefetch(
                "photos",
                queryset = Photo.objects.filter(category = "other").order_by("id"),
                to_attr = "cover_photos",
            )
        )
        .annotate(n_dishes = Count("dishes"))
        .distinct()
    )

    # filtros de platos
    ds_q = (
        Q(name__icontains = q) |
        Q(dish_type__name__icontains = q) |
        Q(dish_type__code__icontains = q) |
        Q(tags__name__icontains = q) |
        Q(tags__code__icontains = q) |
        Q(restaurant__name__icontains = q)
    )

    dishes_qs = (
        Dish.objects
        .filter(ds_q)
        .select_related("restaurant", "dish_type")
        .prefetch_related("tags")
        .distinct()
    )

    restaurants = list(restaurants_qs)
    dishes = list(dishes_qs)

    # agrupamos x restaurant
    restaurant_map = {}
    for r in restaurants:
        restaurant_map[r.id] = {"restaurant": r, "dishes": []}

    for d in dishes:
        rid = d.restaurant_id
        if rid not in restaurant_map:
            restaurant_map[rid] = {"restaurant": d.restaurant, "dishes": []}
        restaurant_map[rid]["dishes"].append(d)

    restaurant_groups = list(restaurant_map.values())

    ctx = {
        "q": q,
        "restaurant_groups": restaurant_groups,
        "counts": {
            "restaurants": len(restaurant_groups),
            "dishes": len(dishes),
        },
    }
    return render(request, "buscar.html", ctx)

def perfil(request):
    return render(request, 'perfil.html')

def favoritos(request):
    return render(request, 'favoritos.html')


def resenas(request):
    return render(request, 'resenas.html')

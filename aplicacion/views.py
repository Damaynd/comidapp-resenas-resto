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
    # armamos query
    q = (request.GET.get("q") or "").strip()

    # si no hay query, mostramos página vacía con el form
    if not q:
        return render(request, "buscar.html", {
            "q": "",
            "restaurants": [],
            "dishes": [],
            "counts": {"restaurants": 0, "dishes": 0},
        })

    # filtros básicos
    # Restaurantes: por nombre, dirección, cocina y tags del local
    rs_q = Q(name__icontains = q) | Q(address__icontains = q) \
           | Q(cuisines__name__icontains = q) \
           | Q(tags__name__icontains = q) | Q(tags__code__icontains = q)

    restaurants = (Restaurant.objects
                   .filter(rs_q)
                   .distinct()
                   .annotate(n_dishes = Count("dishes"))  # útil para mostrar
                   .order_by("name")[:50])

    # Platos: nombre del platillo, tipo de platillo, tags del platillo
    ds_q = Q(name__icontains = q) \
           | Q(dish_type__name__icontains = q) | Q(dish_type__code__icontains = q) \
           | Q(tags__name__icontains = q) | Q(tags__code__icontains = q) \
           | Q(restaurant__name__icontains=q)

    dishes = (Dish.objects
              .filter(ds_q)
              .select_related("restaurant", "dish_type")
              .prefetch_related("tags")
              .distinct()
              .order_by("restaurant__name", "name")[:100])

    ctx = {
        "q": q,
        "restaurants": restaurants,
        "dishes": dishes,
        "counts": {"restaurants": restaurants.count(), "dishes": dishes.count()},
    }
    return render(request, "buscar.html", ctx)

def perfil(request):
    return render(request, 'perfil.html')

def favoritos(request):
    return render(request, 'favoritos.html')


def resenas(request):
    return render(request, 'resenas.html')

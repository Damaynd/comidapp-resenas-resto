from django.shortcuts import render, get_object_or_404, redirect
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
    # parámetros así nomás para el form
    q = (request.GET.get("q") or "").strip()
    rating_min_raw = (request.GET.get("rating_min") or "").strip()
    price_max_raw = (request.GET.get("price_max") or "").strip()
    # support multiple tag and cuisine selections
    tag_raw = (request.GET.get("tag") or "").strip()
    tags_list = request.GET.getlist('tag')
    cuisines_list = request.GET.getlist('cuisine')

    # helpers para el casteo
    def to_int(s):
        try:
            return int(s)
        except ValueError:
            return None

    rating_min = to_int(rating_min_raw) if rating_min_raw else None
    price_max = to_int(price_max_raw) if price_max_raw else None

    # si hay algún criterio seleccionado (incluye listas de tags/cuisines)
    has_filters = any([
        q,
        rating_min is not None,
        price_max is not None,
        tag_raw,
        bool(tags_list),
        bool(cuisines_list),
    ])

    # si no hay filtros ni texto, solo mostramos el formulario sin los resultados
    if not has_filters:
        return render(
            request,
            "buscar.html",
            {
                "q": "",
                "rating_min": "",
                "price_max": "",
                "tag": "",
                "tags": [],
                "cuisines": [],
                "restaurant_groups": [],
                "counts": {"restaurants": 0, "dishes": 0},
            },
        )


    # Base de la query
    restaurants_qs = Restaurant.objects.all()
    dishes_qs = Dish.objects.all()

    # filtro x texto libre
    if q:
        rs_q = (
            Q(name__icontains=q)
            | Q(address__icontains=q)
            | Q(cuisines__name__icontains=q)
            | Q(tags__name__icontains=q)
            | Q(tags__code__icontains=q)
        )
        restaurants_qs = restaurants_qs.filter(rs_q)

        ds_q = (
            Q(name__icontains = q)
            | Q(dish_type__name__icontains = q)
            | Q(dish_type__code__icontains = q)
            | Q(tags__name__icontains = q)
            | Q(tags__code__icontains = q)
            | Q(restaurant__name__icontains = q)
        )
        dishes_qs = dishes_qs.filter(ds_q)

    # filtro x rating mínimo
    if rating_min is not None:
        restaurants_qs = restaurants_qs.filter(avg_rating__gte = rating_min)
        dishes_qs = dishes_qs.filter(restaurant__avg_rating__gte = rating_min)

    # filtro x precio máximo
    if price_max is not None:
        restaurants_qs = restaurants_qs.filter(price__lte = price_max)
        dishes_qs = dishes_qs.filter(restaurant__price__lte = price_max)

    # filtro x tag (soporta múltiples tags)
    if tags_list:
        # exact code match for tags selected
        restaurants_qs = restaurants_qs.filter(tags__code__in = tags_list)
        dishes_qs = dishes_qs.filter(
            Q(tags__code__in = tags_list)
            | Q(restaurant__tags__code__in = tags_list)
        )
    elif tag_raw:
        restaurants_qs = restaurants_qs.filter(
            Q(tags__code__icontains = tag_raw) | Q(tags__name__icontains = tag_raw)
        )
        dishes_qs = dishes_qs.filter(
            Q(tags__code__icontains = tag_raw)
            | Q(tags__name__icontains = tag_raw)
            | Q(restaurant__tags__code__icontains = tag_raw)
            | Q(restaurant__tags__name__icontains = tag_raw)
        )

    # filtro x cuisines (múltiples selecciones)
    if cuisines_list:
        restaurants_qs = restaurants_qs.filter(cuisines__name__in = cuisines_list)
        dishes_qs = dishes_qs.filter(restaurant__cuisines__name__in = cuisines_list)

    # Prefetch y anotaciones
    restaurants_qs = (
        restaurants_qs
        .prefetch_related(
            Prefetch(
                "photos",
                queryset=Photo.objects.filter(category = "other").order_by("id"),
                to_attr = "cover_photos",
            ),
            "tags",
        )
        .annotate(n_dishes = Count("dishes", distinct = True))
        .distinct()
        .order_by("name")
    )

    dishes_qs = (
        dishes_qs
        .select_related("restaurant", "dish_type")
        .prefetch_related("tags")
        .distinct()
        .order_by("restaurant__name", "name")
    )

    restaurants = list(restaurants_qs)
    dishes = list(dishes_qs)


    # Agrupamos x restaurante
    restaurant_map = {}

    # primero los restaurantes que matchean directamente
    for r in restaurants:
        restaurant_map[r.id] = {"restaurant": r, "dishes": []}

    # luego sumamos los restaurantes q aparecen solo x platos
    for d in dishes:
        rid = d.restaurant_id
        if rid not in restaurant_map:
            restaurant_map[rid] = {"restaurant": d.restaurant, "dishes": []}
        restaurant_map[rid]["dishes"].append(d)

    restaurant_groups = list(restaurant_map.values())

    ctx = {
        "q": q,
        "rating_min": rating_min_raw,
        "price_max": price_max_raw,
        "tag": tag_raw,
        "tags": tags_list,
        "cuisines": cuisines_list,
        "restaurant_groups": restaurant_groups,
        "counts": {
            "restaurants": len(restaurant_groups),
            "dishes": len(dishes),
        },
    }
    return render(request, "buscar.html", ctx)

@login_required
def toggle_favorito(request, restaurante_id):
    restaurante = get_object_or_404(Restaurant, id=restaurante_id)
    usuario = request.user

    # Si ya es favorito → lo quita
    if restaurante in usuario.favoritos.all():
        usuario.favoritos.remove(restaurante)
    else:
        usuario.favoritos.add(restaurante)

    return redirect('detalle_restaurante', restaurante_id=restaurante.id)
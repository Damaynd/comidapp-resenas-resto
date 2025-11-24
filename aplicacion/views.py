from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.db.models import Prefetch, Q, Count, Avg
from aplicacion.models import Restaurant, Photo
from .forms import RestaurantReviewForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages

# Para feature/forms se necesitó:
# from django.shortcuts import render, redirect
# from .models import Photo
# from .forms import RestaurantReviewForm
# from django.contrib.auth.decorators import login_required
# from django.db.models import Avg
# from django.db import transaction
# from django.contrib import messages


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
    restaurante = get_object_or_404(Restaurant, pk=restaurante_id)

    form = RestaurantReviewForm()

    return render(request, "detalle_restaurante.html", {
        "restaurante": restaurante,
        "form": form
        })



def buscar(request):
    # parámetros así nomás para el form
    q = (request.GET.get("q") or "").strip()
    rating_min_raw = (request.GET.get("rating_min") or "").strip()
    price_max_raw = (request.GET.get("price_max") or "").strip()
    tag_raw = (request.GET.get("tag") or "").strip()

    # helpers para el casteo
    def to_int(s):
        try:
            return int(s)
        except ValueError:
            return None

    rating_min = to_int(rating_min_raw) if rating_min_raw else None
    price_max = to_int(price_max_raw) if price_max_raw else None

    # si hay algún criterio seleccionado
    has_filters = any([
        q,
        rating_min is not None,
        price_max is not None,
        tag_raw,
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

    # filtro x tag
    if tag_raw:
        restaurants_qs = restaurants_qs.filter(
            Q(tags__code__icontains = tag_raw) | Q(tags__name__icontains = tag_raw)
        )
        dishes_qs = dishes_qs.filter(
            Q(tags__code__icontains = tag_raw)
            | Q(tags__name__icontains = tag_raw)
            | Q(restaurant__tags__code__icontains = tag_raw)
            | Q(restaurant__tags__name__icontains = tag_raw)
        )

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
def resenas(request):
    return render(request, 'resenas.html')

# Si el usuario no ha iniciado sesión, Django lo redirige al Login
@login_required 
def crear_resena(request, restaurante_id):
    # Busca el restaurante. De ser un restaurante con ID inválido: muestra Error 404
    restaurante = get_object_or_404(Restaurant, pk=restaurante_id)

    if request.method == 'POST':
        # Pasamos los datos al modelo de formulario
        # request.POST: para pasar datos; request.FILES: para pasar archivos
        form =RestaurantReviewForm(request.POST, request.FILES)

        # Validaciones automáticas que ofrece Django
        if form.is_valid():
            try:
                # Para prevención de reseña incompleta
                with transaction.atomic():
                    # Guardar Review
                    # commit=False : da el objeto sin guardarlo en BD
                    review = form.save(commit=False)
                    review.restaurant = restaurante
                    review.user = request.user      # Asignamos usuario logueado
                    review.save()                   # Ahora sí guardamos

                    # ------------
                    # Guardar Tags
                    # ------------

                    # Obtener lista Tags marcados
                    selected_tags = form.cleaned_data.get('tags')

                    # Guardar etiquetas dentro de la reseña
                    review.tags.set(selected_tags)

                    # Si hay Tags seleccionados: Añadirlos al modelo del Restaurante
                    if selected_tags:
                        restaurante.tags.add(*selected_tags)

                    # Guardar Foto si existe: Para carrusel
                    if review.photo:
                        Photo.objects.create(
                            uploaded_by=request.user,
                            restaurant=restaurante,
                            category=Photo.Category.OTHER,
                            category_label="Review de Usuario",
                            image = review.photo
                        )

                    # ----------------
                    # Para el promedio
                    # ----------------

                    # Pide a base de datos obtener el promedio de rating
                    nuevo_promedio = restaurante.reviews.aggregate(Avg('rating'))['rating__avg']
                    cantidad_resenas = restaurante.reviews.count()

                    # Guardamos valores en el modelo del restaurante
                    restaurante.avg_rating = round(nuevo_promedio, 1) if nuevo_promedio else 0
                    restaurante.review_count = cantidad_resenas
                    restaurante.save()
                    
                    messages.success(request, "¡Gracias! Tu reseña ha sido publicada.")
                    return redirect('detalle_restaurante', restaurante_id=restaurante_id)
                
            except Exception as e:
                messages.error(request, f"Hubo un error al guardar tu reseña: {e}")
                return redirect('detalle_restaurante', restaurante_id=restaurante_id)

        else:
            print(form.errors)
            messages.error(request, "Error en el formulario. Verifica los datos.")
            return redirect('detalle_restaurante', restaurante_id=restaurante_id)

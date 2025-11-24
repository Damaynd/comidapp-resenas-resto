from django.shortcuts import render, redirect, get_object_or_404
from .models import * 
from django.db.models import Prefetch, Avg
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
    q = request.GET.get('q', '')
    resultados = []  # cambiar por la query real
    return render(request, 'buscar.html', {'q': q, 'resultados': resultados})

def perfil(request):
    return render(request, 'perfil.html')

def favoritos(request):
    return render(request, 'favoritos.html')

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

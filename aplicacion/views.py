from django.shortcuts import render, redirect, get_object_or_404
from .models import * 
from django.db.models import Prefetch
from aplicacion.models import Restaurant, Photo
from .forms import RestaurantReviewForm

# Para feature/forms se necesitó:
# from django.shortcuts import render, redirect
# from .models import Photo
# from .forms import RestaurantReviewForm


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

# Para feature/forms
def crear_resena(request, restaurante_id):
    restaurante = get_object_or_404(Restaurant, pk=restaurante_id)

    if request.method == 'POST':
        # request.POST: para pasar datos; request.FILES: para pasar archivos
        form =RestaurantReviewForm(request.POST, request.FILES)

        # validaciones automáticas que ofrece Django
        if form.is_valid():
            # Guardar Review
            # commit=False : da el objeto sin guardarlo en BD
            review = form.save(commit=False)
            review.restaurant = restaurante
            review.user = request.user      # Asignamos usuario logueado
            review.save()                   # Ahora sí guardamos

            # Guardar Tags
            selected_tags = form.cleaned_data.get('tags')
            for tag in selected_tags:
                restaurante.tags.add(tag)
            
            # Guardar Foto si existe
            uploaded_file = form.cleaned_data.get('photo')
            if uploaded_file:
                Photo.objects.create(
                    uploaded_by=request.user,
                    restaurant=restaurante,
                    category=Photo.Category.OTHER,
                    category_label="Review de Usuario",
                    image = uploaded_file
                )

            return redirect('detalle_restaurante', restaurante_id=restaurante_id)
    
    # Si hay error o no es POST
    return redirect('detalle_restaurante', restaurante_id=restaurante_id)

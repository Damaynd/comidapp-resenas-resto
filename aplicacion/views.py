from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.db.models import Prefetch
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
    q = request.GET.get('q', '')
    resultados = []  # cambiar por la query real
    return render(request, 'buscar.html', {'q': q, 'resultados': resultados})

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
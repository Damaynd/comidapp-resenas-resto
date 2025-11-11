from django.shortcuts import render
from .models import *


# Create your views here.
def home(request):
    lista_restaurantes = Restaurant.objects.all() 
    return render(request, "home.html", {"restaurantes": lista_restaurantes})

# Cuando haces click en un restaurante de home.html, esta funcion te llevara a detalle_restaurante.html para ver mas detalles
def detalle_restaurante(request, restaurante_id):
    restaurante = Restaurant.objects.get(pk=restaurante_id)
    return render(request, "detalle_restaurante.html", {"restaurante": restaurante})

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

def forms(request):
    return render(request, 'forms.html')

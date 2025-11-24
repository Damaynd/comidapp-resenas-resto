from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('restaurantes/<int:restaurante_id>/', views.detalle_restaurante, name='detalle_restaurante'),
    path('buscar/', views.buscar, name='buscar'),
    path('perfil/', views.perfil, name='perfil'),
    path('<int:restaurante_id>/favorito/', views.toggle_favorito, name='toggle_favorito'),
    path('resenas/', views.resenas, name='resenas'),
    # Path con párametro dinámico que reacciona a cada restaurante
    # Carga la de views.py la vista crear_resena
    # name: para usar la ruta en HTML, con apodo abreviado
    path('restaurante/<int:restaurante_id>/crear_resena', views.crear_resena, name='crear_resena')
]

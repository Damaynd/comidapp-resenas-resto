from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('restaurantes/<int:restaurante_id>/', views.detalle_restaurante, name='detalle_restaurante'),
    path('buscar/', views.buscar, name='buscar'),
    path('<int:restaurante_id>/favorito/', views.toggle_favorito, name='toggle_favorito'),
    path('resenas/', views.resenas, name='resenas'),
    # Path con parámetro dinámico que reacciona a cada restaurante
    # Carga la vista `crear_resena` desde views.py
    path('restaurante/<int:restaurante_id>/crear_resena/', views.crear_resena, name='crear_resena'),
]

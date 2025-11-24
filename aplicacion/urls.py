from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('restaurantes/<int:restaurante_id>/', views.detalle_restaurante, name='detalle_restaurante'),
    path('buscar/', views.buscar, name='buscar'),
    path('<int:restaurante_id>/favorito/', views.toggle_favorito, name='toggle_favorito'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('restaurantes/<int:restaurante_id>/', views.detalle_restaurante, name='detalle_restaurante'),
    path('buscar/', views.buscar, name='buscar'),
    path('perfil/', views.perfil, name='perfil'),
    path('favoritos/', views.favoritos, name='favoritos'),
    path('resenas/', views.resenas, name='resenas'),
    # path('formulario/', views.add_restaurant_review, name='formulario'),
    path('restaurante/<int:restaurante_id>/crear_resena', views.crear_resena, name='crear_resena')
]

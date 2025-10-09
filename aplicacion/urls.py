from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("restaurantes/<int:restaurante_id>/", views.detalle_restaurante, name="detalle_restaurante"),
]

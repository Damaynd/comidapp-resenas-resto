from django.urls import path
from . import views
from .views import registro, login_view, logout_view, perfil, favoritos, resenas


urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('favoritos/', favoritos, name='favoritos'),
    path('resenas/', resenas, name='resenas'),
    path('editar/', views.editar_perfil, name='editar_perfil'),
    path('resenas/editar/<int:id>/', views.editar_resena, name='editar_resena'),
    path('resenas/eliminar/<int:id>/', views.eliminar_resena, name='eliminar_resena'),
]

from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from aplicacion.models import Review
from .forms import RegistroUsuarioForm
from django.contrib.auth.decorators import login_required

@login_required
def perfil(request):
    user = request.user
    # Reseñas del usuario
    reseñas = Review.objects.filter(user=user)
    # Restaurantes favoritos (si lo agregas en un ManyToMany en Usuario)
    favoritos = getattr(user, 'favoritos', None)
    return render(request, 'usuarios/perfil.html', {
        'usuario': user,
        'reseñas': reseñas,
        'favoritos': favoritos
    })

def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado correctamente.")
            return redirect('login')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # <--- aquí
        else:
            # mostrar mensaje de error
            return render(request, 'usuarios/login.html', {'error': 'Usuario o contraseña incorrectos'})
    return render(request, 'usuarios/login.html')
def logout_view(request):
    logout(request)
    return redirect('login')

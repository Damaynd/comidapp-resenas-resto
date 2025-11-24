from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from aplicacion.models import Review
from .forms import RegistroUsuarioForm
from django.contrib.auth.decorators import login_required
from .forms import PerfilForm

@login_required
def perfil(request):
    user = request.user
    # Reseñas del usuario
    reseñas = Review.objects.filter(user=user)
    favoritos = user.favoritos.all() 
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

@login_required
def favoritos(request):
    usuario = request.user
    return render(request, 'usuarios/favoritos.html', {
        "favoritos": getattr(usuario, "favoritos", None)
    })

@login_required
def resenas(request):
    usuario = request.user
    resenas_usuario = Review.objects.filter(user=usuario)

    return render(request, 'usuarios/resenas.html', {
        "resenas": resenas_usuario
    })

@login_required
def editar_resena(request, id):
    resena = get_object_or_404(Review, id=id, user=request.user)

    if request.method == "POST":
        contenido = request.POST.get("contenido")
        resena.contenido = contenido
        resena.save()
        return redirect("resenas")

    return render(request, "usuarios/editar_resena.html", {
        "resena": resena
    })

@login_required
def eliminar_resena(request, id):
    resena = get_object_or_404(Review, id=id, user=request.user)

    if request.method == "POST":
        resena.delete()
        return redirect("resenas")

    return render(request, "usuarios/eliminar_resena.html", {
        "resena": resena
    })


@login_required
def editar_perfil(request):
    usuario = request.user

    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = PerfilForm(instance=usuario)

    return render(request, 'usuarios/editar_perfil.html', {'form': form})

@login_required
def favoritos(request):
    usuario = request.user
    favoritos = usuario.favoritos.all()   # ← así se obtienen
    return render(request, 'usuarios/favoritos.html', {"favoritos": favoritos})

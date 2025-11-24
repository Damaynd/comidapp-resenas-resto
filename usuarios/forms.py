from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class RegistroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(
        label="Nombre",
        error_messages={"required": "Por favor ingresa tu nombre."}
    )
    last_name = forms.CharField(
        label="Apellido",
        error_messages={"required": "Por favor ingresa tu apellido."}
    )
    email = forms.EmailField(
        label="Correo electrónico",
        error_messages={
            "required": "Por favor ingresa tu correo electrónico.",
            "invalid": "Ingresa un correo electrónico válido."
        }
    )
    username = forms.CharField(
        label="Nombre de usuario",
        help_text="Requerido. 150 caracteres o menos. Letras, números y @/./+/-/_ solamente.",
        error_messages={"required": "Por favor ingresa un nombre de usuario."}
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        help_text=(
            "Tu contraseña no puede ser muy similar a tu información personal.\n"
            "Debe contener al menos 8 caracteres.\n"
            "No puede ser una contraseña de uso común.\n"
            "No puede ser completamente numérica."
        ),
        error_messages={"required": "Por favor ingresa una contraseña."}
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput,
        help_text="Ingresa la misma contraseña que antes para verificar.",
        error_messages={"required": "Por favor confirma tu contraseña."}
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        error_messages = {
            "password_mismatch": "Las contraseñas no coinciden.",
        }



class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'foto_perfil']

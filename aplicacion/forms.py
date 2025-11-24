from django import forms
from .models import RestaurantReview, Tag

# class RestaurantReviewForm()
#   - Para instanciar el formulario que permite agregar reseña
#   - Hereda de forms.ModelForm: Lo que permite crear un formulario basado en él
class RestaurantReviewForm(forms.ModelForm):

    # Campo para seleccionar tags
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.filter(scope__in=["restaurant", "both"]),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class':'checkboxTags'
            }
        ),
        required=False,
        label='Etiquetas (Opcional)'
    )

    # Clase para configurar el ModelForm
    class Meta:

        # Vincular el formulario a la tabla de la BD
        model = RestaurantReview

        # Campos del modelo que el usuario debe llenar
        fields = ['rating', 'comment', 'photo', 'tags']

        # Para personalizar el HTML que Django generará para cada campo
        widgets = {
            'rating':forms.NumberInput(
                attrs={
                    'class':'rating',
                    'min':'1', # Validación HTML
                    'max':'7',
                    'step': '0.1',
                    'placeholder': '1.0 - 7.0',
                    'oninput': "if(this.value>7) this.value=7; if(this.value<0) this.value=1;" # Validación JS
                }
            ),
            'comment':forms.Textarea(
                attrs={
                    'class':'Textarea',
                    'placeholder':'Escribe tu opinión aquí',
                    'rows': 5
                }
            ),
            'photo': forms.ClearableFileInput(
                attrs={
                    'class':'form-control-file'
                }
            )
        }

        # Para definir labels
        labels = {
            'rating':'Evalúa el lugar (1-7)',
            'comment':'Deja tu comentario',
            'photo': 'Sube una foto (Opcional)'
        }

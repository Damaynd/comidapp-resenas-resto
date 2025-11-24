from django import forms
from .models import RestaurantReview, Tag

class RestaurantReviewForm(forms.ModelForm):

    # Campo para subir una foto
    photo = forms.ImageField(
        required=False,
        label="Sube una foto",
        widget=forms.ClearableFileInput(
            attrs={
                'class':'form-control-file'
            }
        )
    )
    # Campo para seleccionar tags
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.filter(scope__in=["restaurant", "both"]),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class':'checkboxTags'
            }
        ),
        required=False,
        label="Añade etiquetas al restaurante"
    )

    class Meta:
        model = RestaurantReview
        # Campos del modelo que el usuario debe llenar
        fields = ['rating', 'comment']

        widgets = {
            'rating':forms.NumberInput(
                attrs={
                    'class':'rating',
                    'min':1,
                    'max':7
                }
            ),
            'comment':forms.Textarea(
                attrs={
                    'class':'Textarea',
                    'placeholder':'Escribe tu opinión aquí',
                    'rows': 5
                }
            )
        }

        labels = {
            'rating':'Evalúa el lugar (1-7)',
            'comment':'Deja tu comentario',
        }

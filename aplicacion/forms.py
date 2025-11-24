from django import forms
from .models import RestaurantReview, Tag

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
        label="Añade etiquetas al restaurante"
    )

    class Meta:
        model = RestaurantReview
        # Campos del modelo que el usuario debe llenar
        fields = ['rating', 'comment', 'photo', 'tags']

        widgets = {
            'rating':forms.NumberInput(
                attrs={
                    'class':'rating',
                    'min':'1',
                    'max':'7',
                    'step': '0.1',
                    'placeholder': '1.0 - 7.0',
                    'oninput': "if(this.value>7) this.value=7; if(this.value<0) this.value=1;"
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

        labels = {
            'rating':'Evalúa el lugar (1-7)',
            'comment':'Deja tu comentario',
            'tags': 'Etiquetas (Opcional)',
            'photo': 'Sube una foto (Opcional)'
        }
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1:
            raise forms.ValidationError("La calificación mínima es 1.")
        if rating > 7:
            raise forms.ValidationError("La calificación máxima es 7.")
        return rating

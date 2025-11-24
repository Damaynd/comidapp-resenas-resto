from django.contrib import admin
from .models import Restaurant, RestaurantReview, Photo, Tag
from django.utils.html import mark_safe # Para mostrar imágenes reales

# 1. Configuración avanzada para RESEÑAS
class RestaurantReviewAdmin(admin.ModelAdmin):
    # Columnas que se ven en la lista
    list_display = ('restaurant', 'user', 'rating', 'created_at', 'get_tags')
    
    # Filtros laterales (barra derecha)
    list_filter = ('rating', 'created_at', 'restaurant') 
    
    # Barra de búsqueda (puedes buscar por usuario, restaurante o texto del comentario)
    search_fields = ('user__username', 'restaurant__name', 'comment')
    
    # Widget bonito para los tags
    filter_horizontal = ('tags',)
    
    # Campos que no se pueden editar (solo lectura)
    readonly_fields = ('created_at',)

    # Método para mostrar tags en list_display (porque es ManyToMany)
    def get_tags(self, obj):
        return ", ".join([t.name for t in obj.tags.all()])
    get_tags.short_description = 'Etiquetas'


# 2. Configuración avanzada para FOTOS (¡Para ver la imagen en miniatura!)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'category', 'uploaded_by', 'ver_imagen')
    list_filter = ('category', 'created_at')

    # Truco para mostrar la foto real en el admin
    def ver_imagen(self, obj):
        if obj.image:
            # Renderiza HTML seguro
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="border-radius:5px;" />')
        return "Sin imagen"
    ver_imagen.short_description = 'Vista previa'


# 3. Configuración para RESTAURANTES
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'avg_rating', 'review_count', 'price')
    search_fields = ('name', 'address')
    list_filter = ('price',)
    filter_horizontal = ('cuisines', 'tags') # También útil aquí


# --- REGISTRO DE MODELOS ---
# admin.site.register(Modelo, Configuración_Personalizada)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(RestaurantReview, RestaurantReviewAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Tag)
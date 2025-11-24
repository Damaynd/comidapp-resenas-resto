from django.contrib import admin
from .models import Restaurant, RestaurantReview, Photo, Tag # Asegúrate de importar Photo también por si acaso

class RestaurantReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'rating', 'created_at')
    filter_horizontal = ('tags',)
# Si ya tienes Restaurant registrado, añade los otros:
admin.site.register(Restaurant)
admin.site.register(RestaurantReview, RestaurantReviewAdmin)
admin.site.register(Photo)
admin.site.register(Tag)
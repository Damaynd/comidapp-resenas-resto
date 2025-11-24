from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# =========================
# Catálogos
# =========================
class Cuisine(models.Model):
    name = models.CharField(max_length = 100, unique = True)

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """
    Etiquetas unificadas:
      - dietarias (vegan, sin-gluten, etc.)
      - features del local (pet-friendly, accesible, musica-en-vivo, etc.)
    'scope' indica si aplica a restaurantes, platos o a ambos.
    """
    SCOPE = [
        ("restaurant", "restaurant"),
        ("dish", "dish"),
        ("both", "both"),
    ]
    code = models.SlugField(max_length = 100, unique = True)
    name = models.CharField(max_length = 100, unique = True)
    scope = models.CharField(max_length = 20, choices = SCOPE, default = "both")
    group = models.CharField(max_length = 50, blank = True)  # opcional: "dietary" | "feature"

    def __str__(self) -> str:
        return self.name


# =========================
# Platos canónicos (para búsquedas)
# =========================
class DishType(models.Model):
    """
    Plato canónico (p. ej. 'barros-luco', 'papas-fritas').
    Permite buscar por tipo y listar los restaurantes que lo ofrecen.
    """
    code = models.SlugField(max_length = 100, unique = True)
    name = models.CharField(max_length = 100, unique = True)
    category = models.CharField(max_length = 50, blank = True)  # p.ej. 'sandwich', 'acompanamiento', 'entrada'

    def __str__(self) -> str:
        return self.name


class DishTypeAlias(models.Model):
    """
    Sinónimos/alias para un DishType (mejora recall de búsquedas).
    """
    dish_type = models.ForeignKey(DishType, on_delete = models.CASCADE, related_name = "aliases")
    code = models.SlugField(max_length = 100)   # slug alternativo
    name = models.CharField(max_length = 100)   # forma legible alternativa

    class Meta:
        unique_together = ("dish_type", "code")

    def __str__(self) -> str:
        return f"{self.name} → {self.dish_type.name}"


# =========================
# Core
# =========================
class Restaurant(models.Model):
    name = models.CharField(max_length = 100)
    address = models.CharField(max_length = 100)
    lat = models.FloatField()
    lon = models.FloatField()
    price = models.IntegerField(choices = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    url = models.URLField(blank = True, null = True)

    cuisines = models.ManyToManyField(Cuisine, blank = True)
    tags = models.ManyToManyField("Tag", through = "RestaurantTag", blank = True)

    avg_rating = models.FloatField(default = 0)
    review_count = models.IntegerField(default = 0)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self) -> str:
        return self.name


class Dish(models.Model):
    """
    Plato ofrecido por un restaurante. Puede apuntar a un DishType canónico
    para habilitar búsquedas por tipo común (barros-luco, papas-fritas, etc.).
    """
    restaurant = models.ForeignKey(
        Restaurant, on_delete = models.CASCADE, related_name = "dishes"
    )
    dish_type = models.ForeignKey(
        DishType, on_delete = models.SET_NULL, null = True, blank = True, related_name = "restaurant_dishes"
    )
    name = models.CharField(max_length = 100)              # nombre tal cual en la carta del restaurant
    description = models.TextField(blank = True)
    price_ref = models.IntegerField(default = 0)
    tags = models.ManyToManyField("Tag", through = "DishTag", blank = True)

    class Meta:
        unique_together = ("restaurant", "name")

    def __str__(self) -> str:
        base = f"{self.name} @ {self.restaurant.name}"
        return f"{base} [{self.dish_type.name}]" if self.dish_type else base


# =========================
# Relaciones N:M
# =========================
class RestaurantTag(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete = models.CASCADE)

    class Meta:
        unique_together = ("restaurant", "tag")

    def __str__(self) -> str:
        return f"{self.restaurant.name} ⟷ {self.tag.code}"


class DishTag(models.Model):
    dish = models.ForeignKey(Dish, on_delete = models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete = models.CASCADE)
    cross_contamination = models.BooleanField(default = True)

    class Meta:
        unique_together = ("dish", "tag")

    def __str__(self) -> str:
        return f"{self.dish.name} ⟷ {self.tag.code} (cross_contamination = {self.cross_contamination})"


# =========================
# Contenido generado por usuarios
# =========================
class Photo(models.Model):
    class Category(models.TextChoices):
        KITCHEN = "kitchen", "kitchen"
        BATHROOM = "bathroom", "bathroom"
        TABLES = "tables", "tables"
        ENTRANCE = "entrance", "entrance"
        MENU = "menu", "menu"
        DISH = "dish", "dish"
        OTHER = "other", "other"  # categoría comodín

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete = models.CASCADE, null = True, blank = True
    )
    restaurant = models.ForeignKey(
        Restaurant, on_delete = models.CASCADE, related_name = "photos"
    )
    dish = models.ForeignKey(
        Dish, on_delete = models.SET_NULL, null = True, blank = True, related_name = "photos"
    )
    category = models.CharField(max_length = 20, choices = Category.choices)
    # Subtipo libre para 'other' (p. ej., "bar", "fachada", "bebidas")
    category_label = models.CharField(max_length = 50, blank = True)
    path = models.CharField(max_length = 300)
    taken_at = models.DateField(null = True, blank = True)
    is_approved = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add = True)

    def clean(self):
        super().clean()
        if self.category == self.Category.OTHER and not self.category_label:
            raise ValidationError(
                {"category_label": 'Requerido cuando la categoría es "other".'}
            )

    def __str__(self) -> str:
        return f"Photo({self.restaurant.name}, cat = {self.category})"


class Review(models.Model):
    dish = models.ForeignKey(Dish, on_delete = models.CASCADE, related_name = "reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    rating = models.FloatField()
    comment = models.TextField(max_length = 500)
    price_paid = models.IntegerField(default = 0)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        indexes = [
            models.Index(fields = ["dish", "created_at"]),
            models.Index(fields = ["user", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Review({self.user_id} → {self.dish_id}, rating = {self.rating})"


@login_required  
def perfil(request):
    context = {
        'usuario': request.user
    }
    return render(request, 'usuarios/perfil.html', context)
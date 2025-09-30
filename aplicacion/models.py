from django.db import models
from django.conf import settings

class Restaurant(models.Model):
    name = models.CharField(max_length = 100)
    address = models.CharField(max_length = 100)
    lat = models.FloatField()
    lon = models.FloatField()
    price = models.IntegerField(choices = [(1,1),(2,2),(3,3),(4,4),(5,5)])
    url = models.URLField(blank = True, null = True)
    cuisines = models.ManyToManyField(Cuisine, blank = True)
    avg_rating = models.FloatField(default = 0)
    review_count = models.IntegerField(default = 0)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    def __str__(self): return self.name

class Cuisine(models.Model):
    name = models.CharField(max_length = 100)
    def __str__(self): return self.name

class DietaryTag(models.Model):
    code = models.SlugField(max_length = 100, unique = True)
    name = models.CharField(max_length = 100)
    def __str__(self): return self.name

class AccessibilityFeature(models.Model):
    code = models.SlugField(max_length = 100, unique = True)
    name = models.CharField(max_length = 100)
    def __str__(self): return self.name

class Dish(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE, related_name = 'dishes')
    name = models.CharField(max_length = 100)
    description = models.TextField(max_length = 100)
    price_ref = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)
    tags = models.ManyToManyField(DietaryTag, through = "DishDietary", blank = True)

    class Meta:
        unique_together = ('restaurant', 'name')

    def __str__(self): return f"{self.name} @ {self.restaurant.name}"

class DishDietary(models.Model):
    dish = models.ForeignKey(Dish, on_delete = models.CASCADE)
    tag = models.ForeignKey(DietaryTag, on_delete = models.CASCADE)
    evidence = models.CharField(max_length = 20, choices = [("owner", "owner"), ("label", "label"), ("user_report", "user_report")], default = "user_report")
    cross_contamination = models.BooleanField(default = True)

    class Meta:
        unique_together = ('dish', 'tag')

class RestaurantAccessibilityReport(models.Model):
    SOURCE = [("owner", "owner"), ("user", "user")]
    STATUS = [("pending", "pending"), ("accepted", "accepted"), ("rejected", "rejected")]
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE, related_name = 'access_reports')
    feature = models.ForeignKey(AccessibilityFeature, on_delete = models.CASCADE)
    source_type = models.CharField(max_length = 20, choices = SOURCE)
    status = models.CharField(max_length = 20, choices = STATUS, default = "pending")
    notes = models.TextField(blank = True, null = True)
    photo = models.ForeignKey(Photo, on_delete = models.SET_NULL, null = True, blank = True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add = True)

class Review(models.Model):
    dish = models.ForeignKey(Dish, on_delete = models.CASCADE, related_name = 'reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    rating = models.FloatField()
    comment = models.TextField(max_length = 500)
    price_paid = models.IntegerField(default = 0)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        indexes = [models.Index(fields = ['dish', 'created_at']), models.Index(fields = ["user", "created_at"])]
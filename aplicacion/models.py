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
    code = models.SlugField(max_length = 100)
    name = models.CharField(max_length = 100)
    def __str__(self): return self.name


# Create your models here.

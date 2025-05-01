from django.db import models
from .models import *

class ProductAbstractBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class PriceRange(models.Model):
    a = models.FloatField()
    b = models.FloatField()

    def a_to_str(self):
        return str(self.a)

    def __str__(self):
        return f"{self.a} | {self.b}"


class Category(ProductAbstractBase):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Color(ProductAbstractBase):
    title = models.CharField(max_length=50)
    color_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.title
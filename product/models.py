from django.db import models
from product.abstract import *
from django.urls import reverse
from django.utils.text import slugify



class Product(ProductAbstractBase):
    slug = models.SlugField(unique=True, blank=True, null=True)
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    stock = models.IntegerField(default=0)
    price = models.FloatField()
    discount = models.FloatField()
    category = models.ManyToManyField(Category, related_name='product')
    color = models.ManyToManyField(Color, related_name='product')
    is_new = models.BooleanField(default=False)
    is_on_banner = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('products:detail', **{'slug':self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} {self.description[:30]}..."

class ProductRelational(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class ProductImage(ProductRelational):
    image = models.ImageField(upload_to='products_images', null=True, blank=True)

class ProductBanner(ProductRelational):
    image = models.ImageField(upload_to='products_banner_images')

class ProductInformation(ProductRelational):
    text = models.TextField()

    def __str__(self):
        return f'{self.text[:30]}...'

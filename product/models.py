from django.db import models
from product.abstract import *
from accounts.models import User
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
    category = models.ManyToManyField(Category, related_name='category')
    color = models.ManyToManyField(Color, related_name='size')
    is_new = models.BooleanField(default=False)
    is_on_banner = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('product:detail', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_price(self):
        if self.discount:
            return self.price - ((self.price * self.discount) / 100)
        return self.price

    def __str__(self):
        return f"{self.title} {self.description[:30]}..."


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products_images', null=True, blank=True)

class ProductBanner(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products_banner_images')

class ProductInformation(models.Model):
    product = models.ForeignKey(Product, related_name='informations', on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f'{self.text[:30]}...'


class ProductComment(ProductAbstractBase):
    parent = models.ForeignKey(
        'self',
        related_name='productcomment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f"{self.user.username} -> {self.product.title} | {self.comment[:30]}..."
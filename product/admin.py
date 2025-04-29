from django.contrib import admin
from product.models import *
from product.abstract import *

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

class ProductBannerAdmin(admin.StackedInline):
    model = ProductBanner

class ProductInformationAdmin(admin.StackedInline):
    model = ProductInformation

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'stock', 'price', 'discount', 'is_on_banner', 'is_new')
    inlines = (ProductImageAdmin, ProductBannerAdmin , ProductInformationAdmin,)

@admin.register(Category, Color)
class Admin(admin.ModelAdmin):
    pass
from django import template
from django.db.models import Q
from product.models import Product, ProductComment

register = template.Library()

@register.simple_tag
def comment_counter(solo_object):
    return len(ProductComment.objects.filter(Q(product=Product.objects.get(pk=solo_object.id))))

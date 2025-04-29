from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.db.models import Q
from product.models import Product

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/detail.html'
    context_object_name = 'object'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suggestion'] = Product.objects.filter(Q(is_new=True))
        return context
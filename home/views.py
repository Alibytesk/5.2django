from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q
from product.models import Product

class HomeTemplateView(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main'] = Product.objects.filter(Q(is_on_banner=True))
        return context
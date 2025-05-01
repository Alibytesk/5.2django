from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q
from product.models import Product
from product.abstract import PriceRange, Color
from django.core.paginator import Paginator

class HomeTemplateView(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main'] = Product.objects.filter(Q(is_on_banner=True))
        context['items'] = Product.objects.filter(
            Q(pure_title='16thgenerationiPhone') |
            Q(pure_title='macbook') |
            Q(pure_title='airpod')
        )
        context['top3'] = Product.objects.filter(is_top_3=True)
        return context

def render_partial_for_objects_view(request):
    context = {
        'pricerange': PriceRange.objects.all(),
        'colors': Color.objects.all(),
    }
    return render(request, 'includes/filter_search.html', context)
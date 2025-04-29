from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.db.models import Q
from django.urls import reverse
from product.models import Product, ProductComment

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

    def post(self, request, *args, **kwargs):
        comment, parent_id = request.POST.get('comment'), request.POST.get('parent_id')
        self.object = self.get_object()
        if comment:
            ProductComment.objects.create(
                comment=comment,
                parent_id=parent_id if parent_id else None,
                product=self.object,
                user=request.user
            )
        return redirect(reverse('product:detail', kwargs={'slug':self.object.slug}))
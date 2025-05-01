from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models import Q
from django.urls import reverse
from django.core.paginator import Paginator
from product.models import Product, ProductComment, Like

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/detail.html'
    context_object_name = 'object'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object()
        if not self.request.user.is_authenticated:
            context['is_liked'] = False
        else:
            if self.request.user.likes.filter(
                Q(product=self.object) &
                Q(user=self.request.user)
            ).exists():
                context['is_liked'] = True
            else:
                context['is_liked'] = False
        context['suggestion'] = Product.objects.filter(
            Q(discount__in=range(1, 30)) &
            Q(is_new=True)
        )
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

def like(request, slug, id):
    try:
        Like.objects.get(product__slug=slug, user=request.user).delete()
        return JsonResponse(dict({'response':'unliked'}))
    except:
        Like.objects.create(product_id=id, user=request.user)
        return JsonResponse(dict({'response':'liked'}))


def products(request):
    sort_param = request.GET.get('sort')
    if sort_param == 'low-to-high':
        sort = 'price'
    elif sort_param == 'high-to-low':
        sort = '-price'
    else:
        sort = None
    per_page = None
    aprice = request.GET.get('aprice')
    bprice = request.GET.get('bprice')
    color = request.GET.get('color')

    try:
        aprice = float(aprice) if aprice else None
        bprice = float(bprice) if bprice else None
    except ValueError:
        aprice = bprice = None

    if color:
        if aprice is not None and bprice is not None:
            objects = Product.objects.filter(
                Q(pricerange__a__lte=aprice) &
                Q(pricerange__b__gte=bprice) &
                Q(color__title__icontains=color)
            )
        else:
            objects = Product.objects.filter(
                color__title__icontains=color
            )
        per_page = 4

    elif aprice is not None and bprice is not None:
        objects = Product.objects.filter(
            Q(pricerange__a__lte=aprice) &
            Q(pricerange__b__gte=bprice)
        )
        per_page = 4

    else:
        objects = Product.objects.all()

    if sort is not None:
        objects = objects.order_by(sort)

    if per_page is None:
        per_page = 8

    paginator = Paginator(objects, per_page)
    objects = paginator.get_page(request.GET.get('page'))

    context = {
        'objects': objects,
    }
    return render(request, 'product/product_list.html', context)

from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.views.generic import View
from cart.models import *
from product.models import Product

class CartDetailView(View):
    template_name = 'cart/cart.html'

    def get(self, request):
        cart = Cart(self.request)
        return render(request, self.template_name, context={'cart':cart})



class AddToCartView(View):

    def post(self, request, id):
        product = Product.objects.get(pk=id)
        quantity, color = self.request.POST.get('quantity'), self.request.POST.get('color')
        print(quantity, color, product.title)
        cart = Cart(self.request)
        cart.add(product, quantity, color)
        return redirect('product:detail', product.slug)
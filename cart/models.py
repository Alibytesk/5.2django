from django.db import models
from product.models import Product

class Cart:

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get('cart')
        if not self.cart:
            self.cart = self.session['cart'] = dict()

    def __iter__(self):
        cart = self.cart
        for i in cart.values():
            i['product'] = Product.objects.get(pk=int(i['id']))
            i['total'] = (int(i['quantity']) * float(i['price']))
            yield i


    def add(self, product, quantity, color):
        unique = self.unique_id_generator(id=product.id, color=color)
        if not unique in self.cart:
            self.cart[unique] = dict({
                'id': str(product.id),
                'price': str(product.price),
                'discount': str(product.discount),
                'color':color,
                'quantity': int(quantity),
            })
            self.save()
        else:
            self.cart[unique]['quantity'] += int(quantity)
            self.save()

    def save(self):
        self.session.modified = True

    @staticmethod
    def unique_id_generator(id, color):
        return f"{id}{color}"
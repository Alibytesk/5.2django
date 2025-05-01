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
            i['product'] = un_id = Product.objects.get(pk=int(i['id']))
            i['total'] = (int(i['quantity']) * float(i['price']))
            i['un_id'] = self.unique_id_generator(id=un_id.id, color=i['color'])
            if 0 < float(i['discount']):
                i['per_object_total'] = (
                    i['total'] - ((float(i['total']) - float(i['discount'])) / 100)
                )
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

    def delete(self, un_id):
        if self.cart[un_id]:
            del self.cart[un_id]
            self.save()

    def remove_cart(self):
        del self.session['cart']

    def save(self):
        self.session.modified = True

    @staticmethod
    def unique_id_generator(id, color):
        return f"{id}{color}"
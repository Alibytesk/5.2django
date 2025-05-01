from django.urls import path
from cart import views

app_name = 'cart'
urlpatterns = [
    path('add/<int:id>', views.AddToCartView.as_view(), name='add'),
    path('delete/<str:un_id>', views.DeleteFromView.as_view(), name='delete'),
    path('', views.CartDetailView.as_view(), name='cart'),
]
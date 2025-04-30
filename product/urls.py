from django.urls import path
from . import views

app_name = 'product'
urlpatterns = [
    path('detail/<slug:slug>', views.ProductDetailView.as_view(), name='detail'),
    path('like/<slug:slug>/<int:id>', views.like, name='like')
]
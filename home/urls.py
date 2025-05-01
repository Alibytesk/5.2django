from django.urls import path
from home import views

app_name = 'home'
urlpatterns = (
    path('', views.HomeTemplateView.as_view(), name='home'),
    path('render_partial_for_objects_view', views.render_partial_for_objects_view, name='render_partial_for_objects_view'),

)
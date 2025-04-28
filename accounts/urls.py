from django.urls import path
from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('create-account', views.CreateAccountView.as_view(), name='create-account'),
    path('change-password', views.ChangePasswordView.as_view(), name='change-password')
]
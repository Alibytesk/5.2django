from django.urls import path
from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('create-account', views.CreateAccountView.as_view(), name='create-account'),
    path('change-password', views.ChangePasswordView.as_view(), name='change-password'),
    path('email-verify-g', views.GeneratorEmailVerifyView.as_view(), name='email-verify-g'),
    path('email-verify', views.EmailVerifyView.as_view(), name='email-verify'),
    path('forgot-pass', views.ForgotPassView.as_view(), name='forgot-pass'),
    path('forgot-password', views.EmailCheckView.as_view(), name='forgot-password'),
    path('resetpassword/<uidb64>/<str:token>', views.ResetPasswordView.as_view(), name='resetpassword'),
    path('setpassword', views.SetPasswordView.as_view(), name='setpassword')
]
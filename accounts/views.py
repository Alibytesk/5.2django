from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from accounts.models import *
from accounts.forms import *
from accounts.mixins import *
from django.contrib import messages
from django.urls import reverse
from django.utils.crypto import get_random_string
from random import randint

class LoginView(AnonymousRequiredMixin, View):

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            user = authenticate( # accounts/authentication.py
                username=cleaned_data['username'],
                password=cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                messages.success(request, 'successfully login')
                return redirect('home:home')
            else:
                _user_object = User.objects.filter(
                    Q(username__exact=cleaned_data['username']) |
                    Q(email__exact=cleaned_data['username']) |
                    Q(phone__exact=cleaned_data['username'])
                ).first()
                if _user_object:
                    if _user_object.email == cleaned_data['username']:
                        form.add_error('username', 'invalid email or password')
                    elif _user_object.phone == cleaned_data['username']:
                        form.add_error('username', 'invalid phone or password')
                    elif _user_object.username == cleaned_data['username']:
                        form.add_error('username', 'invalid username or password')
                else:
                    form.add_error('username', 'user not found')
        return render(request, 'accounts/authenticate.html', context={'form':form})


    def get(self, request):
            context = {
                'form': LoginForm(),
            }
            return render(request, 'accounts/authenticate.html', context)

class RegisterView(AnonymousRequiredMixin, View):

    def post(self, request):
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            if not User.objects.filter(phone__exact=cleaned_data['phone']).exists():
                if OTPcheck.objects.filter(phone=cleaned_data['phone']).exists():
                    OTPcheck.objects.filter(phone=cleaned_data.get('phone')).delete()
                token, code = get_random_string(length=255), randint(1221, 9889)
                OTPcheck.objects.create(
                    code=code,
                    token=token,
                    phone=cleaned_data['phone']
                )
                request.session['phone'] = cleaned_data['phone']
                return redirect(reverse('accounts:create-account') + f'?token={token}')
            else:
                form.add_error('phone', 'this phone number is already exists')
        return render(request, 'accounts/authenticate.html', context={'form':form})


    def get(self, request):
            context = dict({
                'form': RegisterForm()
            })
            return render(request, 'accounts/authenticate.html', context)

class CreateAccountView(AnonymousRequiredMixin, View):

    def get(self, request):
        OTPcheck.otp_clean()
        if OTPcheck.objects.filter(
                Q(token__exact=request.GET.get('token')) &
                Q(phone=request.session['phone'])
        ).exists():
            form = OTPcheckForm()
            return render(request, 'accounts/authenticate.html', context={'form':form})
        else:
            return redirect('home:home')

    def post(self, request):
        OTPcheck.otp_clean()
        if OTPcheck.objects.filter(
            Q(token__exact=request.GET.get('token')) &
            Q(phone=request.session['phone'])
        ).exists():
            form = OTPcheckForm(data=request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data
                if OTPcheck.objects.filter(code=cleaned_data['code'], phone=request.session['phone']).exists():
                    _user_object = User.objects.filter(
                        Q(username=cleaned_data['username']) |
                        Q(email=cleaned_data['email'])
                    )
                    if not _user_object.exists():
                        if cleaned_data['password1'] == cleaned_data['password2']:
                            User.objects.create_user(
                                username=cleaned_data['username'],
                                email=cleaned_data['email'],
                                phone=request.session['phone'],
                                password=cleaned_data['password1']
                            )
                            del request.session['phone']
                            OTPcheck.objects.filter(token=request.GET.get('token')).delete()
                            return redirect('accounts:login')
                        else:
                            form.add_error('password2', 'passwords does not match')
                    else:
                        q = _user_object.first()
                        if q.email == cleaned_data['email']:
                            form.add_error('email', 'this email is already exists')
                        if q.username == cleaned_data['username']:
                            form.add_error('username', 'this username is already exists')
                else:
                    form.add_error('code', 'invalid code')
            return render(request, 'accounts/authenticate.html', context={'form':form})
        else:
            return redirect('home:home')

class LogoutView(View):

    def get(self, request):
        logout(request)
        messages.success(request, 'successfully logout')
        return redirect('home:home')
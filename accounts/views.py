#accounts.apps
from accounts.models import *
from accounts.forms import *
from accounts.mixins import *

# django
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from django.utils.crypto import get_random_string


# django verification
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site

# python
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

class EmailCheckView(AnonymousRequiredMixin, View):

    def get(self, request):
        form = EmailCheckForm()
        return render(request, 'accounts/authenticate.html', context={'form':form})

    def post(self, request):
        form = EmailCheckForm(data=request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            _user = User.objects.filter(Q(email=cleaned_data['email']))
            if _user.exists():
                user, subject = _user.first(), 'reset your password'
                EmailMessage(
                    subject,
                    render_to_string(
                        template_name='accounts/check_email.html',
                        context={
                            'user':user,
                            'domain':get_current_site(request),
                            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                            'token':default_token_generator.make_token(user)
                        }
                    ),
                    to=[user.email]
                ).send()
                messages.success(request, 'Password reset email has been sent to your email address')
                return redirect('accounts:login')
            else:
                form.add_error('email', 'this email is not exists')
        return render(request, 'accounts/authenticate.html', context={'form':form})

class ResetPasswordView(AnonymousRequiredMixin, View):

    def get(self, request, uidb64, token):
        try:
            u_id = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=u_id)
        except(User.DoesNotExist, ValueError, TypeError, OverflowError):
            user = None
        if user is not None and default_token_generator.check_token(user, token):
            request.session['uid'] = u_id
            messages.success(request, 'reset your password')
            return redirect('accounts:setpassword')
        else:
            messages.error(request, 'The link has been expired')
            return redirect('accounts:login')

class SetPasswordView(AnonymousRequiredMixin, View):

    def post(self, request):
        _user = User.objects.filter(Q(pk=request.session['uid']))
        if _user.exists():
            user = _user.first()
            form = SetPasswordForm(data=request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data
                if cleaned_data['password1'] == cleaned_data['password2']:
                    user.set_password(cleaned_data.get('password1'))
                    user.save()
                    messages.success(request, 'password reset successfully')
                    return redirect('accounts:login')
                else:
                    form.add_error('password1', 'password do not match')
            return render(request, 'accounts/authenticate.html', context={'form':form})
        else:
            return redirect('accounts:login')

    def get(self, request):
        if User.objects.filter(Q(pk=request.session['uid'])).exists():
            form = SetPasswordForm()
            return render(request, 'accounts/authenticate.html', context={'form':form})
        else:
            return redirect('accounts:login')

class ChangePasswordView(LoginRequiredMixin, View):

    def get(self, request):
        form = ChangePasswordForm()
        return render(request, 'accounts/authenticate.html', context={'form':form})

    def post(self, request):
        form = ChangePasswordForm(data=request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            if cleaned_data['password1'] == cleaned_data['password2']:
                user = User.objects.get(phone=request.user.phone)
                if user.check_password(cleaned_data['current_password']):
                    if not cleaned_data['current_password'] == cleaned_data['password1']:
                        user.set_password(cleaned_data['password1'])
                        user.save()
                        messages.success(request, 'password updated successfully')
                        return redirect('accounts:login')
                    else:
                        form.add_error('password1', 'current password and new password are same')
                else:
                    form.add_error('current_password', 'invalid current password')
            else:
                form.add_error('password2', 'password do not match')
        return render(request, 'accounts/authenticate.html', context={'form':form})


class GeneratorEmailVerifyView(LoginRequiredMixin, View):

    def get(self, request):
        VerifyEmailCode.verify_email_code_clean()
        if not request.user.is_email_verify:
            trash = VerifyEmailCode.objects.filter(Q(user__phone__exact=request.user.phone))
            if not trash.exists():
                code, subject = randint(111111, 999999), 'verification email'
                template_name, context,  = 'accounts/verify_email.html', {
                    'code':code,
                    'user':request.user
                }
                EmailMessage(
                    subject,
                    render_to_string(template_name, context),
                    to=[request.user.email]
                ).send()
                messages.success(request, 'email verification has been sent to your email address')
                VerifyEmailCode.objects.create(code=code, user_id=request.user.id).save()
                return redirect('accounts:email-verify')
            else:
                trash.delete()
        else:
            logout(request)
            return redirect('accounts:login')


class EmailVerifyView(LoginRequiredMixin, View):

    def get(self, request):
        VerifyEmailCode.verify_email_code_clean()
        _email_object = VerifyEmailCode.objects.filter(Q(user__phone__exact=request.user.phone))
        if _email_object.exists():
            context = dict({
                'form': VerifyEmailForm()
            })
            return render(request, 'accounts/authenticate.html', context)
        else:
            return redirect('home:home')

    def post(self, request):
        VerifyEmailCode.verify_email_code_clean()
        _email_object = VerifyEmailCode.objects.filter(Q(user__phone__exact=request.user.phone))
        if _email_object.exists():
            form = VerifyEmailForm(data=request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data
                if _email_object.first().code == int(cleaned_data['code']) and _email_object.first().user_id == request.user.id:
                    user = User.objects.filter(
                        Q(phone__exact=request.user.phone) &
                        Q(email__exact=_email_object.first().user.email)
                    ).first()
                    user.is_email_verify = True
                    user.save()
                    _email_object.first().delete()
                    return redirect('home:home')
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

class ForgotPassView(AnonymousRequiredMixin, TemplateView):
    template_name = 'accounts/authenticate.html'
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.validators import MaxLengthValidator, MinLengthValidator
from accounts.models import User
from django.core import validators

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder':'password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder':'password2'})
    )

    class Meta:
        model = User
        fields = ('phone',)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password2 != password1 and password2 and password1:
            raise ValueError('password does not Match')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=True)
        user.set_password(self.cleaned_data.get('password1'))
        user.save()

class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('phone', 'username', 'email', 'password', 'is_active', 'is_admin')


class LoginForm(forms.Form):

    username = forms.CharField(
        widget=forms.TextInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'Your Username, Phone or Email Address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder': 'Password'})
    )

class PhoneValidation:
    @staticmethod
    def is_phone_start_with_09(phone: str):
        if not phone.startswith('09'):
            raise forms.ValidationError('phone should start with 09')

class RegisterForm(forms.Form):

    phone = forms.CharField(
        validators=(validators.MaxLengthValidator(11), PhoneValidation.is_phone_start_with_09,),
        widget=forms.NumberInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'Phone Number'})
    )

class PasswordValidation:
    @staticmethod
    def password_validator(password1):
        errors, special_char = list(), '!@#$%^&*'
        if not password1:
            raise ValueError('users must have a strong password')
        else:
            if not any(i.isdigit() for i in password1):
                errors.append('password must contain at least one number')
            if not any(i in special_char for i in password1):
                errors.append('password must contain at least one special character')
            if not any(i.isupper() for i in password1):
                errors.append('password must contain at least one uppercase character')
            if not any(i.islower() for i in password1):
                errors.append('password must contain at least one lowercase character')
            if len(password1) < 8:
                errors.append('password must be at least 8 character')
            if not errors:
                return password1
            else:
                raise forms.ValidationError(errors)

class OTPcheckForm(forms.Form):
    code = forms.CharField(
        validators=(validators.MaxLengthValidator(4),),
        widget=forms.NumberInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'code'})
    )
    username = forms.CharField(
        validators=(validators.MaxLengthValidator(40), validators.MinLengthValidator(4),),
        widget=forms.TextInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'username'})
    )
    email = forms.EmailField(
        validators=(validators.EmailValidator,),
        widget=forms.EmailInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'Email'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'Password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'Confirmation Password'})
    )

    def clean_password1(self):
        return PasswordValidation.password_validator(self.cleaned_data['password1'])

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'Current-Password'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'new password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'confirmation password'})
    )

    def clean_password1(self):
        return PasswordValidation.password_validator(self.cleaned_data.get('password1'))

class VerifyEmailForm(forms.Form):
    code = forms.CharField(
        validators=(validators.MaxLengthValidator(6), validators.MinLengthValidator(6),),
        widget=forms.NumberInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'code'})
    )

class EmailCheckForm(forms.Form):
    email = forms.CharField(
        validators=(validators.EmailValidator,),
        widget=forms.EmailInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder': 'Enter Your Email'})
    )

class SetPasswordForm(forms.Form):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'new password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'new password confirmation'})
    )

    def clean_password1(self):
        return PasswordValidation.password_validator(self.cleaned_data.get('password1'))

class PhoneCheckForm(forms.Form):
    phone = forms.CharField(
        validators=(MaxLengthValidator(11), MinLengthValidator(11), PhoneValidation.is_phone_start_with_09,),
        widget=forms.NumberInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'Phone Number'})
    )

class CodeCheckForm(forms.Form):
    code = forms.CharField(
        validators=(MaxLengthValidator(6), MinLengthValidator(6),),
        widget=forms.NumberInput(attrs={'class':'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder':'code'})
    )
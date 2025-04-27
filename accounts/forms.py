from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from accounts.models import User

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

class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('phone', 'username', 'email', 'password', 'is_active', 'is_admin')
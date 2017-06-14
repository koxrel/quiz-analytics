from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from quiz_site.form_helpers import BootstrapModelForm


class RegistrationForm(UserCreationForm, BootstrapModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class LoginForm(BootstrapModelForm):
    username = forms.CharField(label=_('Имя пользователя'), max_length=150)
    password = forms.CharField(label=_('Пароль'), widget=forms.PasswordInput)

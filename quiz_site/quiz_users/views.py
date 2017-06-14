from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, reverse
from django.utils.translation import ugettext as _
from django.views import View

from .forms import RegistrationForm, LoginForm


class RegistrationView(View):
    template_name = 'register.html'
    form_class = RegistrationForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            context = {'form': form}
            return render(request, self.template_name, context)

        form.save()
        user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])
        login(request, user)
        return redirect(reverse('quiz:index'))


class LoginView(View):
    template_name = 'login.html'
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                if 'next' in request.GET:
                    return redirect(request.GET['next'])
                return redirect(reverse('quiz:index'))
            else:
                error = _('Пользователь с такой парой логин/пароль не найден.')
        else:
            context = {'form': form}
            return render(request, self.template_name, context)
        context = {'form': form, 'error': error}
        return render(request, self.template_name, context)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('quiz:index'))

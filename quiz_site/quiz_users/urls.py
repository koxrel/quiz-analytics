from django.conf.urls import url
from . import views

app_name = 'quiz_users'
urlpatterns = [
    url(r'^register$', views.RegistrationView.as_view(), name='register'),
    url(r'^login$', views.LoginView.as_view(), name='login'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),
]

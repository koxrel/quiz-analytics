from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from . import views

app_name = 'analytics'
urlpatterns = [
    url(r'^(?P<quiz_name>[\w-]+)$', staff_member_required(views.SummaryQuizView.as_view()), name='summary'),
    url(r'^(?P<quiz_name>[\w-]+)/(?P<username>.+)$', staff_member_required(views.UserQuizView.as_view()), name='user'),
    url(r'^$', staff_member_required(views.QuizListView.as_view()), name='list')
]
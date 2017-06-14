from django.conf.urls import url
from .views import QuizDetailView, QuizTake, IndexView


app_name = 'quiz'
urlpatterns = [
    url(r'^(?P<slug>[\w-]+)/$', QuizDetailView.as_view(), name='detail'),
    url(r'^(?P<quiz_name>[\w-]+)/take/$', QuizTake.as_view(), name='take'),
    url(r'^$', IndexView.as_view(), name='index')
]

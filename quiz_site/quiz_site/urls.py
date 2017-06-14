from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/report/', include('analytics.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('quiz_users.urls')),
    url(r'^', include('quiz.urls'))
]

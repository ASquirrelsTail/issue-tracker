"""ticket_tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import os
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
from django.conf import settings
from account import urls as account_urls
from tickets import urls as tickets_urls
from credits import urls as credits_urls
from stats import urls as stats_urls
from stats.views import IndexView, RoadmapView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^account/', include(account_urls)),
    url(r'^tickets/', include(tickets_urls)),
    url(r'^credits/', include(credits_urls)),
    url(r'^stats/', include(stats_urls)),
    url(r'^roadmap/$', RoadmapView.as_view(), name='roadmap'),
    url(r'^$', IndexView.as_view(), name='index'),
]

# If local static is set, or there is no AWS access key use local media storage
if 'LOCAL_STATIC' in os.environ or not settings.AWS_ACCESS_KEY_ID:
    urlpatterns.append(url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}))

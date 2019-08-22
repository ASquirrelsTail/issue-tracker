from django.conf.urls import url, include
from django.contrib.auth import urls as auth_urls

urlpatterns = [
    url(r'^', include(auth_urls)),
]

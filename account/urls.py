from django.conf.urls import url, include
from django.contrib.auth import urls as auth_urls
from account.views import SignUp, LogIn

urlpatterns = [
    url(r'^login/$', LogIn.as_view(), name='login'),
    url(r'^sign-up/$', SignUp.as_view(), name='signup'),
    url(r'^', include(auth_urls)),
]

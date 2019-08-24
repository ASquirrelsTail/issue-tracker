from django.conf.urls import url, include
from django.contrib.auth import urls as auth_urls
from account.views import SignUp, LogIn

urlpatterns = [
    url(r'^', include(auth_urls)),
    url(r'^sign-up/$', SignUp.as_view(), name='signup'),
    url(r'^login/$', LogIn.as_view(), name='login'),
]

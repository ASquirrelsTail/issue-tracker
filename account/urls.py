from django.conf.urls import url, include
from django.contrib.auth import urls as auth_urls
from account.views import SignUp

urlpatterns = [
    url(r'^', include(auth_urls)),
    url(r'^sign-up$', SignUp.as_view(), name='signup'),
]

from django.urls import path
from .views import *

urlpatterns = [
    path('create-admin', CreateAdminAPI.as_view(), name="CreateAdminAPI"),
    path('login-admin', LoginAdminAPI.as_view(), name="LoginAdminAPI"),


]
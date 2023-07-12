from django.urls import path
from .views import *

urlpatterns = [
    path('register-user', RegisterUserAPI.as_view(), name="RegisterUserAPI"),
    path('add-member', AddFamilyMembersAPI.as_view(), name="AddFamilyMembersAPI"),
    path('user-login', UserLoginAPI.as_view(), name="UserLoginAPI"),
    path('profile-view', ViewProfileAPI.as_view(), name="ViewProfileAPI"),
    path('profile-edit', EditProfileAPI.as_view(), name="EditProfileAPI"),



]
from django.urls import path
from .views import *

urlpatterns = [
    #------------------- Register User --------------------#
    path('register-user', RegisterUserAPI.as_view(), name="RegisterUserAPI"),

    #------------------- Add / Delete Family Members -------------#
    path('add-member', AddandDeleteFamilyMembersAPI.as_view(), name="AddandDeleteFamilyMembersAPI"),
    path('delete-member', AddandDeleteFamilyMembersAPI.as_view(), name="AddandDeleteFamilyMembersAPI"),

    #------------------- Login User ------------------------#
    path('user-login', UserLoginAPI.as_view(), name="UserLoginAPI"),

    #------------ User Profile View, Update and Delete ----------#
    path('profile-view', UserProfileAPI.as_view(), name="UserProfileAPI"),
    path('profile-edit', UserProfileAPI.as_view(), name="UserProfileAPI"),
    path('profile-delete', UserProfileAPI.as_view(), name="UserProfileAPI"),

]
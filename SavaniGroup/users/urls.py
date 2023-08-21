from django.urls import path
from .views import *

urlpatterns = [
    #------------------- Register User --------------------#
    path('register-user', RegisterUserAPI.as_view(), name="RegisterUserAPI"),

    #------------------- Verify mobile number --------------------#
    path('verify-mobile' , VerifyMobilenumber.as_view() , name='VerifyMobilenumber'),

    #------------------- Add / Delete Family Members -------------#
    path('add-member', AddandDeleteFamilyMembersAPI.as_view(), name="AddandDeleteFamilyMembersAPI"),
    path('delete-member', AddandDeleteFamilyMembersAPI.as_view(), name="AddandDeleteFamilyMembersAPI"),

    #------------------ List Family Members -----------------#
    path('family-members', ListFamilyMembersAPI.as_view(), name="ListFamilyMembersAPI"),

    #------------------- User login and logout ------------------------#
    path('user-login', UserLogin.as_view(), name="UserLogin"),
    path('login-verify', UserLoginVerify.as_view() , name='UserLoginVerify'),

    #------------ User Profile View, Update and Delete ----------#
    path('profile-view', UserProfileAPI.as_view(), name="UserProfileAPI"),
    path('profile-edit', UserProfileAPI.as_view(), name="UserProfileAPI"),
    path('profile-delete', UserProfileAPI.as_view(), name="UserProfileAPI"),

    #--------------- Upload Student Results ---------------------#
    path('upload-result', UploadResultAPI.as_view(), name="UploadResultAPI"),


]
from django.urls import path
from .views import *

urlpatterns = [
    #------------------- Register User --------------------#
    path('register-user', RegisterUserAPI.as_view(), name="RegisterUserAPI"),

    #------------------- Verify email --------------------#
    path('verify-email' , VerifyOtp.as_view() , name='VerifyOtp'),

    #------------------- Resend otp --------------------#
    path('resend-otp' , ResendOtp.as_view() , name='ResendOtp'),

    #------------------- Add / Delete Family Members -------------#
    path('add-member', AddandDeleteFamilyMembersAPI.as_view(), name="AddandDeleteFamilyMembersAPI"),
    path('delete-member', AddandDeleteFamilyMembersAPI.as_view(), name="AddandDeleteFamilyMembersAPI"),

    #------------------ List Family Members -----------------#
    path('family-members', ListFamilyMembersAPI.as_view(), name="ListFamilyMembersAPI"),

    #------------------- Login User ------------------------#
    path('user-login', UserLoginAPI.as_view(), name="UserLoginAPI"),

    #------------ User Profile View, Update and Delete ----------#
    path('profile-view', UserProfileAPI.as_view(), name="UserProfileAPI"),
    path('profile-edit', UserProfileAPI.as_view(), name="UserProfileAPI"),
    path('profile-delete', UserProfileAPI.as_view(), name="UserProfileAPI"),

]
from django.urls import path
from .views import *

urlpatterns = [

    #---------------------- Create Admin ----------------------#
    path('create-admin', CreateAdminAPI.as_view(), name="CreateAdminAPI"),

    #----------------------- Login Admin ----------------------#
    path('login-admin', LoginAdminAPI.as_view(), name="LoginAdminAPI"),

    #----------------- View/Update Admin Profile --------------#
    path('admin-profile-view', AdminProfileAPI.as_view(), name="AdminProfileAPI"),
    path('admin-profile-edit', AdminProfileAPI.as_view(), name="AdminProfileAPI"),

    #------------------ Get All Community Members -------------#
    path('list-community-members', GetAllCommunityMembersAPI.as_view(), name="GetAllCommunityMembersAPI"),
    path('get-edit-delete-member' , GetEditDeleteCommunityMemberAPI.as_view() , name='GetEditDeleteCommunityMemberAPI'),

    #------------------- Approve Community Members ------------#
    path('approve-member', ApproveCommunityMembersAPI.as_view(), name="ApproveCommunityMembersAPI"),

    #------------------- Add Authority Members ------------#
    path('add-user-auth-member', AddUserorAuthorityMembersAPI.as_view(), name="AddUserorAuthorityMembersAPI"),

    #------------------ Get All President shri -------------#
    path('authority-members',GetAllAuthorityMembersAPI.as_view() , name='GetAllAuthorityMembersAPI'),

    #------------------- Add Donators ------------#
    path('add-donators' , AddDonatorAPI.as_view() , name='AddDonatorAPI'),

    #------------------- Add earning , expenses and interest ------------#
    path('add-get-earning' , AddAndGetEarningAPI.as_view() , name='AddAndGetEarningAPI'),
    path('add-expenses' , AddExpensesAPI.as_view() , name='AddExpensesAPI'),
    path('add-interest' , AddInterestAPI.as_view() , name='AddInterestAPI'),

    path('send-message' , SendMessageAPI.as_view() , name='SendMessageAPI'),

]
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

    #------------------ Add user ----------------#
    # path('add-user' , AddUserorAuthorityMembersAPI.as_view() , name='AddUserorAuthorityMembersAPI'),

    #------------------- Approve Community Members ------------#
    path('approve-member', ApproveCommunityMembersAPI.as_view(), name="ApproveCommunityMembersAPI"),

    #------------------- Add Authority Members ------------#
    path('add-auth-member', AddAuthorityMembers.as_view(), name="AddAuthorityMembers"),

    #------------------ Get All President shri -------------#
    path('president-shre',GetAllPresidentShree.as_view() , name='GetAllPresidentShree'),

    path('send-message' , SendMessageAPI.as_view() , name='SendMessageAPI'),

]
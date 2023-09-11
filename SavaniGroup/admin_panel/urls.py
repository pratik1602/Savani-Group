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
    path('community-member-details' , GetDetailsOfCommunityMemberAPI.as_view() , name='GetDetailsOfCommunityMemberAPI'),

    #------------------ Add Community Services ----------------#
    # path('add-community-service', AddCommunitySerivicesAPI.as_view(), name="AddCommunitySerivicesAPI"),

    #------------------ Get Community Servives ----------------# (ADMIN, USER)
    # path('get-community-service', GetCommunityServicesAPI.as_view(), name="GetCommunityServicesAPI"),

    #------------------- Approve Community Members ------------#
    path('approve-member', ApproveCommunityMembersAPI.as_view(), name="ApproveCommunityMembersAPI"),

    #------------------- Add Authority Members ------------#
    path('add-auth-member', AddAuthorityMembers.as_view(), name="AddAuthorityMembers"),

    #------------------ Get All President shri -------------#
    path('president-shre',GetAllPresidentShree.as_view() , name='GetAllPresidentShree'),

]
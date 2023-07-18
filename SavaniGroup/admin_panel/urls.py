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

    #------------------ Add Community Services ----------------#
    path('add-community-service', AddCommunitySerivicesAPI.as_view(), name="AddCommunitySerivicesAPI"),






]
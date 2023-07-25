from django.shortcuts import render
from pymongo import MongoClient
from decouple import config
from rest_framework.views import APIView
from datetime import datetime
import re
from django.contrib.auth.hashers import make_password, check_password
from bson.objectid import ObjectId
from core.response import *
from core.authentication import *
from .utils import *

# Mongo client for making connection with database 
client = MongoClient(config('MONGO_CONNECTION_STRING'))

# Creating database
db = client.Savani_Group

def valueEntity(item) -> dict:
    if item is not None:
        for key, value in item.items():
            if ObjectId.is_valid(value):
                item[key] = str(item[key])
        return item
    return None

def valuesEntity(entity) -> list:
    return [valueEntity(item) for item in entity]


#---------------------- Create Admin Account -------------------#

class CreateAdminAPI(APIView):

    def post(self, request):
        data = request.data
        if data['firstname'] != '' and len(data['firstname']) >= 3:
            if data['lastname'] != '' and len(data['lastname']) >= 3:
                if len(data['mobile_no']) == 10 and re.match("[6-9][0-9]{9}", data['mobile_no']):
                    if data['email'] != '' and re.match("^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$", data["email"]):
                        if data["password"] == data["confirm_password"]:
                            existingUser = db.community_members.find_one({'$or': [{"mobile_no": data["mobile_no"]}, {"email": data["email"]}]})
                            if not existingUser:
                                obj = {
                                    "firstname": data['firstname'],
                                    "lastname": data['lastname'],
                                    "password": make_password(data["password"], config("PASSWORD_KEY")),
                                    "mobile_no": data['mobile_no'],
                                    "email": data['email'],
                                    "profile_pic": "",
                                    "is_admin": False,
                                    "is_active": False,
                                    "createdAt": datetime.datetime.now(),
                                    "updatedAt": "",
                                }
                                db.admin.insert_one(obj)
                                return onSuccess("Admin Regitration Successful...", 1)
                            else:
                                return badRequest("User already exist with same mobile or email, Please try again.")
                        else:
                            return badRequest("Password and Confirm password doesn't matched.")
                    else:
                        return badRequest("Invalid email id, Please try again.")
                else:
                    return badRequest("Invalid mobile number, Please try again.")
            else:
                return badRequest("Invalid last name, Please try again.")
        else:
            return badRequest("Invalid first name, Please try again.")


#---------------------------- Login Admin -----------------------#

class LoginAdminAPI(APIView):

    def post(self, request):
        data = request.data
        if (data['username'] != '' and len(data['username']) == 10 and re.match("[6-9][0-9]{9}", data['username'])) or (data['username'] != '' and re.match("^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$", data["username"])):
            if data['password'] != '' and len(data['password']) >= 8:
                get_admin = db.admin.find_one({"$or": [{"mobile_no": data["username"]}, {"email": data["username"]}]})
                if get_admin is not None:
                    checkPassword = check_password(data['password'], get_admin['password'])
                    if checkPassword:
                        db.admin.update_one({"_id": ObjectId(get_admin["_id"])}, {"$set": {"is_active": True, "is_admin": True}})
                        token = create_access_token(get_admin["_id"])
                        return onSuccess("Admin Login successful.", token)
                    else:
                        return badRequest("Password is Incorrect.")
                else:
                    return badRequest("Admin not found or Invalid")
            else:
                return badRequest("Invalid Password")
        else:
            return badRequest("Invalid mobile number or email.")
        

#-------------------------- View/Update Admin Profile -------------------#

class AdminProfileAPI(APIView):

    def get(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            get_admin = valueEntity(db.admin.find_one({"_id": ObjectId(token["_id"]), "is_active":True, "is_admin" : True}, {"_id": 0,"password": 0,  "is_admin" : 0, "createdAt": 0,"updatedAt": 0}))
            if get_admin is not None:
                return onSuccess("Admin profile!", get_admin)
            else:
                return badRequest("Admin not found")
        else:
            return unauthorisedRequest()

    def post(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            data = request.data
            get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]), "is_active":True, "is_admin" : True})
            if get_admin is not None:
                new_obj = {"$set": {
                    "firstname": data["firstname"],
                    "lastname": data["lastname"],
                    "profile_pic": "",
                    "updatedAt": datetime.datetime.now(),
                    "updatedBy": ObjectId(token["_id"]),
                }
                }
                updateUser = db.admin.find_one_and_update({"_id": ObjectId(get_admin["_id"])}, new_obj)
                if updateUser:
                    updatedUser = valueEntity(db.admin.find_one({"_id": ObjectId(get_admin["_id"])}, {"_id": 0,"password": 0,  "is_admin" : 0, "createdAt": 0, "updatedBy":0}))
                    return onSuccess("Profile updated successfully!", updatedUser)
                else:
                    return badRequest("Invalid data to update profile, Please try again.")
            else:
                return badRequest("Admin not found")
        else:
            return unauthorisedRequest()


#----------------------- Get All Community Members ---------------------#

class GetAllCommunityMembersAPI(APIView):

    def get(self, request):
        token =  authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]), "is_active":True, "is_admin" : True})
            if get_admin is not None:
                role = request.GET.get("role")
                if role != None or 0:
                    get_all_members = valuesEntity(db.community_members.find({"role": role}, {"password": 0, "updatedAt": 0, "updatedBy": 0}).sort("createdAt", -1))
                    if get_all_members:
                        return onSuccess("All users based on filter.", get_all_members)
                    else:
                        return badRequest("No Users Found based on filter.")
                else:
                    get_all_members = valuesEntity(db.community_members.find({},{"password": 0, "updatedAt": 0, "updatedBy": 0}).sort("createdAt", -1))
                    if get_all_members:
                        return onSuccess("Community Members List", get_all_members)
                    else:
                        return badRequest("No Members found.")
            else:
                return badRequest("Admin not found.")
        else:
            return unauthorisedRequest()


#--------------------- Add Community Services --------------------#
# from io import BytesIO


class AddandGetCommunitySerivicesAPI(APIView):

    def post(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            data = request.data
            get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]), "is_active":True, "is_admin" : True})
            if get_admin is not None:
                pdf = request.FILES["pdf_form"]
                pdf_url = upload_pdf_to_cloudinary(pdf)
                obj = {
                    "scheme_name": data["scheme_name"],
                    "pdf_form": pdf_url,
                    "createdBy": ObjectId(token["_id"]),
                    "createdAt": datetime.datetime.now(),
                    "updatedAt": "",
                }
                db.community_services.insert_one(obj)
                return onSuccess("Scheme added successfully.", 1)
            else:
                return badRequest("Admin not found.")
        else:
            return unauthorisedRequest()


#--------------------------- Get Community Servives --------------------# (ADMIN, USER)

class GetCommunityServicesAPI(APIView):

    def get(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            get_user = db.admin.find_one({"_id": ObjectId(token["_id"]), "is_active":True, "is_admin" : True}) or db.community_members.find_one({"_id": ObjectId(token["_id"]), "is_active":True}) 
            if get_user is not None:
                get_Community_services = valuesEntity(db.community_services.find())
                if get_Community_services:
                    return onSuccess("Community services.", get_Community_services)
                else:
                    return badRequest("No Community services found.")
            else:
                return badRequest("Admin not found.")
        else:
            return unauthorisedRequest()


#------------------------------ Approve Community Members -----------------------#

class ApproveCommunityMembersAPI(APIView):

    def post(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]),"is_active":True, "is_admin" : True})
            if get_admin is not None:
                data = request.data
                if ObjectId().is_valid(data["_id"]):
                    get_community_member = db.community_members.find_one({"_id": ObjectId(data["_id"]), "is_active": True, "registration_fee": True})
                    if get_community_member:
                        obj = {"$set": {
                            "is_approved": data["is_approved"]
                        }   
                        }
                        db.community_members.find_one_and_update({"_id": ObjectId(get_community_member["_id"])}, obj)
                        return onSuccess("Communiy member approved successfully.", 1)
                    else:
                        return badRequest("Community member not found or not active or not paid registration fees.")
                else:
                    return badRequest("user id is invalid.")
            else:
                return badRequest("Admin not found.")
        else:
            return unauthorisedRequest()


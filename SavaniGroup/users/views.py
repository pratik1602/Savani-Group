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
from django.core import serializers

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

# # Creating Collections (Tables)
# community_members = db.community_members
# accounts = db.account

#----------------- Sign-Up User API ------------------# (USER)

class RegisterUserAPI(APIView):
    def post(self, request):
        data = request.data
        if data['firstname'] != '' and len(data['firstname']) >= 3:
            if data['lastname'] != '' and len(data['lastname']) >= 3:
                if len(data['mobile_no']) == 10 and re.match("[6-9][0-9]{9}", data['mobile_no']):
                    if data['email'] != '' and re.match("^[a-zA-Z0-9-_.]+@[a-zA-Z0-9]+\.[a-z]{1,3}$", data["email"]):
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
                                    "is_approved": False,
                                    "is_active": False,
                                    "role": "parent_user",
                                    "registration_fee": False,
                                    "createdAt": datetime.datetime.now(),
                                    "updatedAt": "",
                                    "createdBy": "",
                                    "updatedBy": "",
                                }
                                db.community_members.insert_one(obj)
                                return onSuccess("Regitration Successful...", 1)
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


#-------------------------- Login User ----------------------------# (USER)

class UserLoginAPI(APIView):
    def post(self, request):
        data = request.data
        if (data['username'] != '' and len(data['username']) == 10 and re.match("[6-9][0-9]{9}", data['username'])) or (data['username'] != '' and re.match("^[a-zA-Z0-9-_.]+@[a-zA-Z0-9]+\.[a-z]{1,3}$", data["username"])):
            if data['password'] != '' and len(data['password']) >= 8:
                get_user = db.community_members.find_one({"$or": [{"mobile_no": data["username"]}, {"email": data["username"]}], "is_approved": True})
                if get_user is not None:
                    checkPassword = check_password(data['password'], get_user['password'])
                    if checkPassword:
                        db.community_members.update_one({"_id": ObjectId(get_user["_id"])}, {"$set": {"is_active": True}})
                        token = create_access_token(get_user["_id"])
                        return onSuccess("Login successful.", token)
                    else:
                        return badRequest("Password is Incorrect.")
                else:
                    return badRequest("User not found or Invalid or not approved.")
            else:
                return badRequest("Invalid Password")
        else:
            return badRequest("Invalid mobile number or email.")


#--------------------------- Add/Delete Family Members -------------------------# (PARENT USER)

class AddandDeleteFamilyMembersAPI(APIView):
    def post(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            data = request.data
            parent_user = db.community_members.find_one({"_id": ObjectId(token["_id"]), "role": "parent_user"})
            if parent_user:
                if data['firstname'] != '' and len(data['firstname']) >= 3:
                    if data['lastname'] != '' and len(data['lastname']) >= 3:
                        if len(data['mobile_no']) == 10 and re.match("[6-9][0-9]{9}", data['mobile_no']):
                            if data['email'] != '' and re.match("^[a-zA-Z0-9-_.]+@[a-zA-Z0-9]+\.[a-z]{1,3}$", data["email"]):
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
                                            "is_approved": False,
                                            "is_active": False,
                                            "role": "child_user",
                                            "registration_fee": True,
                                            "createdAt": datetime.datetime.now(),
                                            "updatedAt": "",
                                            "createdBy": parent_user["_id"],
                                            "updatedBy": "",
                                        }
                                        db.community_members.insert_one(obj)
                                        return onSuccess("Family Member Added Successfully...", 1)
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
            else:
                return badRequest("Root User not found.")
        else:
            return unauthorisedRequest()
        
    def delete(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            data = request.data
            parent_user = db.community_members.find_one({"_id": ObjectId(token["_id"]), "role": "parent_user"})
            if parent_user:
                get_member = db.community_members.find_one({"_id": ObjectId(data["_id"]), "role": "child_user"})
                if get_member:
                    db.community_members.delete_one(get_member)
                    return onSuccess("Member deleted successfully.", 1)
                else:
                    return badRequest("Member not found.")
            else:
                return badRequest("Root user not found.")
        else:
            return unauthorisedRequest()


#----------------------- List of Family Members ----------------------# (PARENT USER)

class ListFamilyMembersAPI(APIView):

    def get(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            parent_user = db.community_members.find_one({"_id": ObjectId(token["_id"]), "is_approved": True, "is_active":True, "registration_fee": True, "role": "parent_user"})
            if parent_user:
                filter = {"createdBy": ObjectId(parent_user["_id"])}
                family_members = valuesEntity(db.community_members.find(filter, {"_id": 0, "password": 0, "createdBy": 0, "updatedBy": 0, "is_approved": 0, "createdAt": 0,"updatedAt": 0, "is_active": 0, "role":0}))
                if family_members:
                    return onSuccess("Family Members List.", family_members)
                else:
                    return badRequest("No Family Members found.")
            else:
                return badRequest("Root user not found.")
        else:
            return unauthorisedRequest()


#----------------------- User Profile View, Update and Delete -------------------------# (USER)

class UserProfileAPI(APIView):

    def get(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            userData = valueEntity(db.community_members.find_one({"_id": ObjectId(token["_id"]), "is_approved": True, "is_active":True, "registration_fee": True}, {"password": 0, "createdBy": 0, "updatedBy": 0, "is_approved": 0, "createdAt": 0,"updatedAt": 0}))
            if userData is not None:
                return onSuccess("User profile!", userData)
            else:
                return badRequest("User not found")
        else:
            return unauthorisedRequest()

    def post(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            data = request.data
            userData = db.community_members.find_one({"_id": ObjectId(token["_id"]), "is_approved": True, "is_active":True, "registration_fee": True})
            if userData is not None:
                new_obj = {"$set": {
                    "firstname": data["firstname"],
                    "lastname": data["lastname"],
                    "profile_pic": "",
                    "updatedAt": datetime.datetime.now(),
                    "updatedBy": ObjectId(token["_id"]),
                }
                }
                updateUser = db.community_members.find_one_and_update({"_id": ObjectId(token["_id"])}, new_obj)
                if updateUser:
                    updatedUser = valueEntity(db.community_members.find_one({"_id": ObjectId(token["_id"])}, {"password": 0, "createdBy": 0, "updatedBy": 0, "is_approved": 0, "createdAt": 0,"updatedAt": 0}))
                    return onSuccess("Profile updated successfully!", updatedUser)
                else:
                    return badRequest("Invalid data to update profile, Please try again.")
            else:
                return badRequest("User not found.")
        else:
            return unauthorisedRequest()

    def delete(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            get_user = db.community_members.find_one({"_id": ObjectId(token["_id"]), "is_approved": True, "is_active":True, "registration_fee": True})
            if get_user:
                db.community_members.delete_one(get_user)
                return onSuccess("Profile deleted successfully.", 1)
            else:
                return badRequest("User not found.")
        else:
            return unauthorisedRequest()
        

#--------------------------- Apply for Community Services -----------------------#

# class ApplyForCommunityServicesAPI(APIView):

#     def 

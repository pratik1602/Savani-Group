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

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
        if (data['username'] != '' and len(data['username']) == 10 and re.match("[6-9][0-9]{9}", data['username'])) or (data['username'] != '' and re.match("^[a-zA-Z0-9-_.]+@[a-zA-Z0-9]+\.[a-z]{1,3}$", data["username"])):
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
                get_all_members = valuesEntity(db.community_members.find({"is_approved":True}, {"_id": 1,"firstname": 1,"middlename": 1,"lastname": 1,"country_code": 1,"mobile_no": 1,"role": 1,"is_approved": 1,"createdAt": 1}).sort("createdAt", -1))
                return onSuccess('All community members' , get_all_members)
            else:
                return badRequest("Admin not found.")
        else:
            return unauthorisedRequest()
        
class GetEditDeleteCommunityMemberAPI(APIView):

    def get(self , request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token['_id']):
            get_admin = db.admin.find_one({'_id':ObjectId(token['_id']) , 'is_active':True , 'is_admin':True})
            if get_admin is not None and get_admin:
                _id = request.GET.get('_id')
                if _id and ObjectId().is_valid(_id):
                    get_user = valueEntity(db.community_members.find_one({'_id':ObjectId(_id) , 'role':'parent_user'} , {'iso_code':0,'mobile_otp':0,'login_otp':0,'is_active':0,'mobile_verified':0,'createdAt':0,'updatedAt':0,'createdBy':0,'updatedBy':0,}))
                    if get_user is not None and get_user:
                        get_family_members = valuesEntity(db.community_members.find({'createdBy':ObjectId(get_user['_id']) , 'role':'child_user'} , {'createdAt':0,'updatedAt':0,'createdBy':0,'updatedBy':0,'role':0}))
                        if get_family_members:
                            data = {
                                'Parent user': get_user,
                                'Family members': get_family_members
                            }
                            return onSuccess('Details of user' , data)
                        else:
                            data = {
                                'Parent user': get_user,
                                'Family members': []
                            }
                            return onSuccess('Details of user' , data)
                    else:
                        return badRequest('User not found.')
                else:
                    return badRequest('Bad request.')
            else:
                return badRequest('Admin not found.')
        else:
            return unauthorisedRequest()
        
    def delete(self , request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token['_id']):
            get_admin = db.admin.find_one({'_id':ObjectId(token['_id']) , 'is_active':True , 'is_admin':True})
            if get_admin is not None and get_admin:
                _id = request.GET.get('_id')
                if _id and ObjectId().is_valid(_id):
                    get_user = db.community_members.find_one({'_id':ObjectId(_id) , 'role':'parent_user'})
                    if get_user and get_user is not None:
                        db.community_members.delete_one({'_id':ObjectId(get_user['_id']) , 'role':'parent_user'})
                        db.community_members.delete_many({'createdBy':ObjectId(get_user['_id']) , 'role':'child_user'})
                        db.community_services.delete_many({'createdBy':ObjectId(get_user['_id'])})
                        db.student_results.delete_many({'createdBy':ObjectId(get_user['_id'])})
                        return onSuccess('User delete successfully.' , 1)
                    else:
                        return badRequest('User not found.')
                else:
                    return badRequest('Id not found.')
            else:
                return badRequest('Admin not found.')
        else:
            return unauthorisedRequest()
        
#------------------------------ Add user -----------------------#

# class AddUserorAuthorityMembersAPI(APIView):
#     def post(self , request):
#         role = ['user' , 'village_head' , 'taluka_head' , 'president']
#         token = authenticate(request)
#         if token and ObjectId().is_valid(token["_id"]):
#             get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]),"is_active":True, "is_admin" : True})
#             if get_admin is not None:
#                 data = request.data
#                 if data['fullname'] and data['country_code'] and data['iso_code'] and data['mobile_no'] and data['role']:
#                     if data['role'] in role and data['role'].isalpha():
#                         if data['role'] == 'user':
#                             existingUser = db.community_members.find_one({"country_code": data['country_code'],"iso_code": data['iso_code'], "mobile_no": data['mobile_no']})
#                             if not existingUser:
#                                 obj = {
#                                     "firstname": data['firstname'],
#                                     "middlename": data['middlename'],
#                                     "lastname": "Savani",
#                                     "country_code": data['country_code'],
#                                     "iso_code": data['iso_code'],
#                                     "mobile_no": data['mobile_no'],
#                                     "is_approved": True,
#                                     "is_active": False,
#                                     "registration_fees": True,
#                                     "mobile_verified": True,
#                                     "role": "parent_user",
#                                     "createdAt": datetime.datetime.now(),
#                                     "updatedAt": "",
#                                     "createdBy": get_admin['_id'],
#                                     "updatedBy": "",
#                                 }
#                                 db.community_members.insert_one(obj)
#                                 return onSuccess('User added successfully.' , 1)
#                             else:
#                                 return badRequest('User already exist with same mobile, Please try again.')
#                         elif data['role'] == 'village_head':
#                             return
#                         elif data['role'] == 'taluka_head':
#                             return
#                         elif data['role'] == 'president':
#                             return
#                         else:
#                             return badRequest('Invalid role type.')
#                     else:
#                         return badRequest('Invalid role type.')                     
#                 else:
#                     return badRequest('All fields are necessary to fill.')
#             else:
#                 return badRequest("Admin not found.")
#         else:
#             return unauthorisedRequest()


#------------------------------ Approve Community Members -----------------------#

class ApproveCommunityMembersAPI(APIView):

    def post(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]),"is_active":True, "is_admin" : True})
            if get_admin is not None:
                data = request.data
                if data['_id'] and ObjectId().is_valid(data["_id"]):
                    get_community_member = db.community_members.find_one({"_id": ObjectId(data["_id"]), "is_active": True, "registration_fee": True})
                    if get_community_member:
                        obj = {"$set": {
                            "is_approved": data["is_approved"]
                            }   
                        }
                        db.community_members.find_one_and_update({"_id": ObjectId(get_community_member["_id"])}, obj)
                        return onSuccess("Community member approved successfully.", 1)
                    else:
                        return badRequest("Community member not found or not active or not paid registration fees.")
                else:
                    return badRequest("user id is invalid.")
            else:
                return badRequest("Admin not found.")
        else:
            return unauthorisedRequest()

#------------------------------ Add/Delete authority members -----------------------#

class AddAuthorityMembers(APIView):

    def post(self , request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token['_id']): 
            get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]),"is_active":True, "is_admin" : True})
            if get_admin is not None:
                data = request.data
                if data['firstname'] and data['firstname'] != '' and len(data['firstname']) >= 3:
                    if data['middlename'] and data['middlename'] != '':
                        if data['villagename'] and data['villagename'] != '':
                            if data['role'] and data['role'] != '':
                                if data['designation']:
                                    obj = {
                                        "firstname": data['firstname'],
                                        "middlename": data['middlename'],
                                        "lastname": 'Savani',
                                        "village": data['villagename'],
                                        "role": data['role'],
                                        "designation": data['designation'],
                                        "authority_person": True,
                                        "is_active": False,
                                        "createdAt": datetime.datetime.now(),
                                        "createdBy": get_admin['_id'],
                                        "updatedAt": "",
                                        "updatedBy": "",
                                    }
                                    db.community_members.insert_one(obj)
                                    return onSuccess("Add successfully",1)
                                else:
                                    return badRequest('Invalid designation, Please try again.')
                            else:
                                return badRequest('Invalid role, Please try again.')
                        else:
                            return badRequest('Invalid village name, Please try again.')
                    else:
                        return badRequest('Invalid middle name, Please try again.')
                else:
                    return badRequest('Invalid firstname, Please try again.')                        
            else:
                return badRequest('Admin not found.')
        else:
            return unauthorisedRequest()

class GetAllPresidentShree(APIView):
    def get(self , request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token['_id']):
            get_user = db.community_members.find_one({"_id": ObjectId(token["_id"]) , "is_active":True}) or db.admin.find_one({"_id": ObjectId(token["_id"]) , "is_active":True , "is_admin": True})
            if get_user is not None:
                role = request.GET.get('role')
                if role and role != '':
                    get_all_president = valuesEntity(db.community_members.find({"role": role}, {"authority_person": 0, "createdAt": 0 , "createdBy": 0 , "is_active": 0 , "_id": 0 , "updatedAt": 0, "updatedBy": 0}).sort("createdAt", -1))
                    return onSuccess("List of all authority members",get_all_president)
                else:
                    return badRequest('Invalid role, Please try again.')
            else:
                return badRequest('User not found.')
        else:   
            return unauthorisedRequest()
        
class SendMessageAPI(APIView):

    def post(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token['_id']):
            get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]),"is_active":True, "is_admin" : True})
            if get_admin:
                data = request.data
                if data['subject'] and data['message']:
                    obj = {
                        'subject': data['subject'],
                        'message': data['message'],
                        "createdAt": datetime.datetime.now(),
                        "createdBy": get_admin['_id'],
                        "updatedAt": "",
                        "updatedBy": "",
                    }
                    notification = db.SendMessages.insert_one(obj)
                    # print('notification :',notification)
                    if notification:
                        channel_layer = get_channel_layer()
                        data = {
                            'subject': data['subject'],
                            'message': data['message']
                        }
                        async_to_sync(channel_layer.group_send)(
                            'User_notification',
                            {
                                'type': 'send.message',
                                'data': data,
                            }
                        )
                        return onSuccess('Message send successfully.' , 1)
                    else:
                        return notCreated('Please try again.')
                else:
                    return badRequest('All the fields are necessary to fill.')
            else:
                return badRequest('Admin not found.')
        else:
            return unauthorisedRequest()
from django.shortcuts import render
from pymongo import MongoClient , ReturnDocument
from decouple import config
from rest_framework.views import APIView
from datetime import datetime
import re , math , random
from django.contrib.auth.hashers import make_password, check_password
from bson.objectid import ObjectId
from core.response import *
from core.authentication import *
from django.core import serializers
from .utils import send_otp , verify_otp

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

#generate otp
def generateOTP() :
    digits = "0123456789"
    OTP = ""
    for i in range(6) :
        OTP += digits[math.floor(random.random() * 10)]
 
    return OTP

#----------------- Sign-Up User API ------------------# (USER)

class RegisterUserAPI(APIView):
    def post(self, request):
        blood_group = ['A+' , 'A-' , 'B+' , 'B-' , 'O+' , 'O-' , 'AB+' , 'AB-']
        data = request.data
        if data['firstname'] != '' and len(data['firstname']) >= 3:
            if data["middlename"] != '' and len(data["middlename"]) >= 3:
                if data["gender"] and (data["gender"] == 'male' or data["gender"] == 'female'):
                    if data["dob"]:
                        if data["address"]:
                            if data["occupation"] and (data["occupation"] == 'business' or data['occupation'] == 'job' or data['occupation'] == 'other'):
                                if data["education"]:
                                    if data["blood_group"] and (data["blood_group"] in blood_group):
                                        if data["district"]:
                                            if data["taluka"]:
                                                if data["village_name"]:
                                                    if data["marital_status"] and (data["marital_status"] == 'married' or data["marital_status"] == 'unmarried'):
                                                        if data["aadhar_number"] and len(data["aadhar_number"]) == 12 and data['aadhar_number'].isnumeric():
                                                            if data['country_code'] and re.match(r'^\+\d{1,3}$' , data['country_code']):
                                                                if data['iso_code'] and data['iso_code'].isalpha() and (len(data['iso_code']) == 2 or len(data['iso_code']) == 3):
                                                                    if data['mobile_no'].isnumeric() and data['mobile_no'] and data['mobile_no'] != '':
                                                                        if data['email'] != '' and re.match("^[a-zA-Z0-9-_.]+@[a-zA-Z0-9]+\.[a-z]{1,3}$", data["email"]):
                                                                            existingUser = db.community_members.find_one({'$or': [{"mobile_no": data["mobile_no"]}, {"email": data["email"]}, {"aadhar_number": data["aadhar_number"]}]})
                                                                            if not existingUser:
                                                                                obj = {
                                                                                    "profile_pic": "",
                                                                                    "firstname": data['firstname'],
                                                                                    "middlename": data["middlename"],
                                                                                    "lastname": "Savani",
                                                                                    "gender": data["gender"],
                                                                                    "dob": data["dob"],
                                                                                    "email": data['email'],
                                                                                    "country_code": data['country_code'],
                                                                                    "iso_code": data['iso_code'],
                                                                                    "mobile_no": data['mobile_no'],
                                                                                    "address": data["address"],
                                                                                    "occupation": data["occupation"],
                                                                                    "education": data["education"], 
                                                                                    "blood_group" : data["blood_group"],
                                                                                    "district": data["district"],
                                                                                    "taluka": data["taluka"],
                                                                                    "village_name": data["village_name"],
                                                                                    "marital_status": data["marital_status"],
                                                                                    "aadhar_number": data["aadhar_number"],
                                                                                    # "password": make_password(data["password"], config("PASSWORD_KEY")),
                                                                                    "mobile_otp": generateOTP(),
                                                                                    "login_otp" : "",
                                                                                    "is_approved": False,
                                                                                    "is_active": False,
                                                                                    "registration_fees": False,
                                                                                    "mobile_verified": False,
                                                                                    "role": "parent_user",
                                                                                    "createdAt": datetime.datetime.now(),
                                                                                    "updatedAt": "",
                                                                                    "createdBy": "",
                                                                                    "updatedBy": "",
                                                                                }
                                                                                db.community_members.insert_one(obj)
                                                                                mobile_number = obj["country_code"]+obj["mobile_no"]
                                                                                mobile_otp = obj["mobile_otp"]
                                                                                send_otp(mobile_number,mobile_otp)
                                                                                return onSuccess("Regitration Successful...", 1)
                                                                            else:
                                                                                return badRequest("User already exist with same mobile or email, Please try again.")
                                                                        else:
                                                                            return badRequest("Invalid email id, Please try again.")
                                                                    else:
                                                                        return badRequest("Invalid mobile number, Please try again.")
                                                                else:
                                                                    return badRequest("Invalid iso code, Please try again.")
                                                            else:
                                                                return badRequest("Invalid country code,Please try again.")
                                                        else:
                                                            return badRequest("Invalid aadhar number, Please try again.")
                                                    else:
                                                        return badRequest("Invalid marital status, Please try again.")
                                                else:
                                                    return badRequest("Invalid village name, Please try again.")
                                            else:
                                                return badRequest("Invalid taluka, Please try again.")
                                        else:
                                            return badRequest("Invalid district, Please try again.")
                                    else:
                                        return badRequest("Invalid blood group, Please try again.")
                                else:
                                    return badRequest("Invalid education, Please try again.")
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
        
#-------------------------- Verify mobile number ----------------------------# (USER)
class VerifyMobilenumber(APIView):
    def post(self , request):
        data = request.data
        if data['country_code'] and re.match(r'^\+\d{1,3}$' , data['country_code']):
            if data['mobile_no'].isnumeric() and data['mobile_no'] and data['mobile_no'] != '':
                if data['otp'] and data['otp'] != '' and len(data['otp']) == 6 and data['otp'].isnumeric():
                    user = db.community_members.find_one({"country_code" : data['country_code'] , "mobile_no" : data['mobile_no']})
                    if user is not None:
                        if not user['mobile_verified']:
                            mobile_number = user['country_code'] + user['mobile_no']
                            otp =  data['otp']
                            mobile_verified = verify_otp(mobile_number , otp)
                            if mobile_verified:
                                new_obj = {
                                    "$set": {
                                        "mobile_verified": True,
                                        "updatedAt": datetime.datetime.now(),
                                    }
                                }
                                updateUser = db.community_members.find_one_and_update({"_id": user['_id']} , new_obj , return_document=ReturnDocument.AFTER)
                                if updateUser:
                                    return onSuccess("Mobile number verified successfully." , 1)
                                else:
                                    return badRequest("Invalid data to verify mobile number, Please try again.")
                            else:
                                return badRequest("Invalid data to verify mobile number, Please try again.")
                        else:
                            return badRequest("Your number is already verified.")
                    else:
                        return badRequest("User does not exist with this mobile number.")
                else:
                    return badRequest("Invalid otp, Please try again.")
            else:
                return badRequest("Invalid mobile number, Please try again.")
        else:
            return badRequest("Invalid country code, Please try again.")


#-------------------------- User login and logout ----------------------------# (USER)
class UserLogin(APIView):
    def post(self , request):
        data = request.data
        if data['country_code'] and re.match(r'^\+\d{1,3}$' , data['country_code']):
            if data['mobile_no'].isnumeric() and data['mobile_no'] and data['mobile_no'] != '':
                get_user = db.community_members.find_one({"country_code" : data['country_code'] , "mobile_no" : data['mobile_no']})
                if get_user is not None:
                    if get_user['mobile_verified']:
                        if get_user['is_approved']:
                            new_obj = {
                                "$set": {
                                    "login_otp": generateOTP(),
                                    "updatedAt": datetime.datetime.now(),
                                }
                            }
                            update_user = db.community_members.find_one_and_update({"country_code" : data['country_code'] , "mobile_no" : data['mobile_no']} , new_obj , return_document=ReturnDocument.AFTER)
                            mobile_no = update_user['country_code']+update_user['mobile_no']
                            otp = update_user['login_otp']
                            send = send_otp(mobile_no , otp)
                            if send:
                                return onSuccess("OTP send successfully.",1)
                            else:
                                return badRequest("Invalid data to send otp, Please try again.")
                        else:
                            return badRequest("Not approved, Please wait for admin approval.")
                    else:
                        return badRequest("Mobile number is not verified, Please verify first.")
                else:
                    return badRequest("User with this number not exits.")
            else:
                return badRequest("Invalid mobile number, Please try again.")
        else:
            return badRequest("Invalid country code,Please try again.")

class UserLoginVerify(APIView):
    def post(self,request):
        data = request.data
        if data['country_code'] and re.match(r'^\+\d{1,3}$' , data['country_code']):
            if data['mobile_no'].isnumeric() and data['mobile_no'] and data['mobile_no'] != '':
                if data['otp'] and data['otp'] != '' and len(data['otp']) == 6 and data['otp'].isnumeric():
                    user = db.community_members.find_one({"country_code" : data['country_code'] , "mobile_no" : data['mobile_no']})
                    if user is not None:
                        if user['mobile_verified']:
                            if user['is_approved']:
                                mobile_number = user['country_code'] + user['mobile_no']
                                otp = data['otp']
                                verify = verify_otp(mobile_number , otp)
                                if verify:
                                    new_obj = {
                                        "$set": {
                                            "is_active": True,
                                            "updatedAt": datetime.datetime.now(),
                                        }
                                    }
                                    updateUser = db.community_members.find_one_and_update({"_id": user['_id']} , new_obj , return_document=ReturnDocument.AFTER)
                                    if updateUser:
                                        new_token = create_access_token(updateUser['_id'])
                                        return onSuccess("Login successfully.",new_token)
                                    else:
                                        return badRequest('Invalid data to login, Please try again.')
                                else:
                                    return badRequest("Invalid otp, Please try again.")
                            else:
                                return badRequest('Not approved, Please wait for admin approval.')
                        else:
                            return badRequest('Mobile number is not verified.')
                    else:
                        return badRequest('User not found.')
                else:
                    return badRequest('Invalid otp, Please try again.')
            else:
                return badRequest("Invalid mobile number, Please try again.")
        else:
            return badRequest("Invalid country code, Please try again.") 

#--------------------------- Add/Delete Family Members -------------------------# (PARENT USER)

class AddandDeleteFamilyMembersAPI(APIView):
    def post(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            data = request.data
            parent_user = db.community_members.find_one({"_id": ObjectId(token["_id"]), "role": "parent_user"})
            if parent_user:
                if data['fullname'] != '' and data['fullname'].isalpha():
                    if data['relation'] and data['relation'] != '' and  data['relation'].isalpha():
                        if data["marital_status"] and (data["marital_status"] == 'married' or data["marital_status"] == 'unmarried'):
                            if data["education"]:
                                if data["occupation"] and (data["occupation"] == 'business' or data['occupation'] == 'job' or data['occupation'] == 'other'):
                                    if data["aadhar_number"] and len(data["aadhar_number"]) == 12 and data['aadhar_number'].isnumeric():
                                        existingUser = db.community_members.find_one({'aadhar_number': data["aadhar_number"]})
                                        if not existingUser:
                                            obj = {
                                                "fullname": data['fullname'],
                                                # "lastname": data['lastname'],
                                                # "password": make_password(data["password"], config("PASSWORD_KEY")),
                                                "relation": data["relation"],
                                                "dob": data["dob"],
                                                "marital_status": data["marital_status"],
                                                "education": data["education"],
                                                "occupation": data["occupation"],
                                                "aadhar_number": data["aadhar_number"],
                                                # "mobile_no": data['mobile_no'],
                                                # "email": data['email'],
                                                # "profile_pic": "",
                                                # "is_approved": False,
                                                # "is_active": False,
                                                "role": "child_user",
                                                # "registration_fee": True,
                                                "createdAt": datetime.datetime.now(),
                                                "updatedAt": "",
                                                "createdBy": parent_user["_id"],
                                                "updatedBy": "",
                                            }
                                            db.community_members.insert_one(obj)
                                            return onSuccess("Family Member Added Successfully...", 1)
                                        else:
                                            return badRequest("Family member already exist.")
                                    else:
                                        return badRequest("Invalid aadhar number, Please try again.")
                                else:
                                    return badRequest("Invalid occupation, Please try again.")
                            else:
                                return badRequest('Invalid education, Please try again.')
                        else:
                            return badRequest("Invalid marital status, Please try again.")
                    else:
                        return badRequest("Invalid relation, Please try again.")
                else:
                    return badRequest("Invalid name, Please try again.")
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
            parent_user = db.community_members.find_one({"_id": ObjectId(token["_id"]), "is_approved": True, "is_active":True, "registration_fees": True, "role": "parent_user"})
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
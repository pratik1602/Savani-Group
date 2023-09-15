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
from core.utils import is_date_grater_than , is_date_less_than , is_date_less_than_or_equal_today , is_date_grater_than_or_equal_today , validate_date_formate , get_start_and_end_date

from users.views import generateOTP

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
                get_all_members = valuesEntity(db.community_members.find({"$or" : [{"role": "parent_user"} ,{"role": "village_head"} ,{"role": "taluka_head"} ,{"role": "president"}]}, {"_id": 1,"firstname": 1,"middlename": 1,"lastname": 1,"country_code": 1,"mobile_no": 1,"role": 1,"is_approved": 1,"createdAt": 1}).sort("createdAt", -1))
                data = {
                    'total_user': len(get_all_members),
                    'user_details': get_all_members
                }
                return onSuccess('All community members' , data)
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

class AddUserorAuthorityMembersAPI(APIView):
    def post(self , request):
        role = ['user' , 'village_head' , 'taluka_head' , 'president']
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]),"is_active":True, "is_admin" : True})
            if get_admin is not None:
                data = request.data
                if data['firstname'] and data['middlename'] and data['country_code'] and data['iso_code'] and data['mobile_no'] and data['role']:
                    if data['role'] in role:
                        if data['role'] == 'user':
                            existingUser = db.community_members.find_one({"country_code": data['country_code'],"iso_code": data['iso_code'], "mobile_no": data['mobile_no']})
                            if not existingUser:
                                obj = {
                                    "profile_pic": "",
                                    "firstname": data['firstname'],
                                    "middlename": data["middlename"],
                                    "lastname": "Savani",
                                    "gender": "",
                                    "dob": "",
                                    "country_code": data['country_code'],
                                    "iso_code": data['iso_code'],
                                    "mobile_no": data['mobile_no'],
                                    "address": "",
                                    "occupation": "",
                                    "education": "",
                                    "blood_group": "",
                                    "district": "",
                                    "taluka": "",
                                    "village_name": "",
                                    "marital_status": "",
                                    "aadhar_number": "",
                                    "mobile_otp": generateOTP(),
                                    "login_otp": "",
                                    "is_approved": True,
                                    "is_active": False,
                                    "registration_fees": True,
                                    "mobile_verified": True,
                                    "role": "parent_user",
                                    "createdAt": datetime.datetime.now(),
                                    "updatedAt": "",
                                    "createdBy": get_admin['_id'],
                                    "updatedBy": "",
                                }
                                db.community_members.insert_one(obj)
                                return onSuccess('User added successfully.' , 1)
                            else:
                                return badRequest('User already exist with same mobile, Please try again.')
                        elif data['role'] == 'village_head':
                            if data['village_name']:
                                existingVillagehead = db.community_members.find_one({'village_name': data['village_name'].lower() , 'role': 'village_head'})
                                if not existingVillagehead: 
                                    obj = {
                                        "firstname": data['firstname'],
                                        "middlename": data['middlename'],
                                        "lastname": "Savani",
                                        "country_code": data['country_code'],
                                        "iso_code": data['iso_code'],
                                        "mobile_no": data['mobile_no'],
                                        "village_name": data['village_name'].lower(),
                                        "role": "village_head",
                                        "is_approved" : True,
                                        "authority_person": True,
                                        "createdAt": datetime.datetime.now(),
                                        "updatedAt": "",
                                        "createdBy": get_admin['_id'],
                                        "updatedBy": "",
                                    }
                                    db.community_members.insert_one(obj)
                                    return onSuccess('Village head added successfully.' , 1)
                                else:
                                    return badRequest('Village head already exits.')
                            else:
                                return badRequest('Please enter village name.')
                        elif data['role'] == 'taluka_head':
                            if data['taluka_name']:
                                existingTalukahead = db.community_members.find_one({'taluka': data['taluka_name'].lower() , 'role': 'taluka_head'})
                                if not existingTalukahead: 
                                    obj = {
                                        "firstname": data['firstname'],
                                        "middlename": data['middlename'],
                                        "lastname": "Savani",
                                        "country_code": data['country_code'],
                                        "iso_code": data['iso_code'],
                                        "mobile_no": data['mobile_no'],
                                        "taluka": data['taluka_name'].lower(),
                                        "role": "taluka_head",
                                        "is_approved" : True,
                                        "authority_person": True,
                                        "createdAt": datetime.datetime.now(),
                                        "updatedAt": "",
                                        "createdBy": get_admin['_id'],
                                        "updatedBy": "",
                                    }
                                    db.community_members.insert_one(obj)
                                    return onSuccess('Taluka head added successfully.' , 1)
                                else:
                                    return badRequest('Taluka head already exits.')
                            else:
                                return badRequest('Please enter taluka name.')
                        elif data['role'] == 'president':
                            if data['village_name']:
                                if data['designation']:
                                    existingPresident = db.community_members.find_one({'role': 'president' , 'designation': data['designation'].lower()})
                                    if not existingPresident: 
                                        obj = {
                                            "firstname": data['firstname'],
                                            "middlename": data['middlename'],
                                            "lastname": "Savani",
                                            "country_code": data['country_code'],
                                            "iso_code": data['iso_code'],
                                            "mobile_no": data['mobile_no'],
                                            "village_name": data['village_name'].lower(),
                                            "role": "president",
                                            "designation": data['designation'].lower(),
                                            "is_approved" : True,
                                            "authority_person": True,
                                            "createdAt": datetime.datetime.now(),
                                            "updatedAt": "",
                                            "createdBy": get_admin['_id'],
                                            "updatedBy": "",
                                        }
                                        db.community_members.insert_one(obj)
                                        return onSuccess('President added successfully.' , 1)
                                    else:
                                        return badRequest('President already exits.')
                                return badRequest('Invalid designation.')
                            else:
                                return badRequest('Invalid village name.')
                        else:
                            return badRequest('Invalid role type.')
                    else:
                        return badRequest('Invalid role type.')                     
                else:
                    return badRequest('All fields are necessary to fill.')
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

#------------------------------ Get authority members -----------------------#

class GetAllAuthorityMembersAPI(APIView):
    def get(self , request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token['_id']):
            get_user = db.community_members.find_one({"_id": ObjectId(token["_id"]) , "is_active":True}) or db.admin.find_one({"_id": ObjectId(token["_id"]) , "is_active":True , "is_admin": True})
            if get_user is not None:
                role = request.GET.get('role')
                if role and role != '':
                    get_all_president = valuesEntity(db.community_members.find({"role": role , "authority_person":True}, {"authority_person": 0, "createdAt": 0 , "createdBy": 0 , "is_active": 0 , "_id": 0 , "updatedAt": 0, "updatedBy": 0 , "date": 0, "amount": 0, "online": 0,"transactionID": 0,"role": 0}).sort("createdAt", -1))
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

class AddDonatorAPI(APIView):
    def post(self , request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]),"is_active":True, "is_admin" : True})
            if get_admin is not None:
                data = request.data
                if data['donator_name'] and data['village_name'] and data['date'] and data['amount']:
                    if data['online'] == True:
                        if data['transactionID'] and data['transactionID'] != '' and (' 'not in data['transactionID']):
                            obj = {
                                "donator_name": data['donator_name'],
                                "village_name": data['village_name'],
                                "date": data['date'],
                                "amount": data['amount'],
                                "online": data['online'],
                                "transactionID": data['transactionID'],
                                "role": "donator",
                                "authority_person": True,
                                "createdAt": datetime.datetime.now(),
                                "updatedAt": "",
                                "createdBy": get_admin['_id'],
                                "updatedBy": "",
                            }
                            db.community_members.insert_one(obj)
                            return onSuccess('Donator added successfully.',1)
                        else:
                            return badRequest('Invalid transactionID.')
                    else:
                        obj = {
                            "donator_name": data['donator_name'],
                            "village_name": data['village_name'],
                            "date": data['date'],
                            "amount": data['amount'],
                            "online": False,
                            "transactionID": "",
                            "role": "donator",
                            "authority_person": True,
                            "createdAt": datetime.datetime.now(),
                            "updatedAt": "",
                            "createdBy": get_admin['_id'],
                            "updatedBy": "",
                        }
                        db.community_members.insert_one(obj)
                        return onSuccess('Donator added successfully.',1)
                else:
                    return badRequest("All the fields are necessary to fill.")
            else:
                return badRequest("Admin not found.")
        else:
            return unauthorisedRequest()


class AddAndGetEarningAPI(APIView):

    def get(self , request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token['_id']):
            get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]),"is_active":True, "is_admin" : True})
            if get_admin is not None:
                month = request.GET.get('month')
                year = request.GET.get('year')
                if month and year:
                    start_date , end_date = get_start_and_end_date(month=int(month) , year=int(year))
                    total_amount = 0
                    month_earning = valuesEntity(db.earnings_expenses.find({"type": "earning" , "createdAt":{"$gte": start_date,"$lt": end_date}} , {"createdAt": 0 , "createdBy": 0 , "updatedAt": 0, "updatedBy": 0 , "type":0}).sort("createdAt", -1))
                    earing_details = valuesEntity(db.earnings_expenses.find({"type": "earning"} , {"createdAt": 0 , "createdBy": 0 , "updatedAt": 0, "updatedBy": 0 , "type":0}).sort("createdAt", -1))
                    for earning in month_earning:
                        total_amount += earning['amount']
                    data = {
                        'total_amount':total_amount,
                        'earing_details': earing_details
                    }
                    return onSuccess('total earning',data)
                else:
                    current_year = datetime.datetime.today().year
                    start_date = datetime.datetime(current_year , 1 , 1)
                    end_date = datetime.datetime(current_year , 12 , 31)
                    current_year_earning_amount = 0
                    current_year_expenses_amount = 0
                    current_year_earning_details = valuesEntity(db.earnings_expenses.find({"type": "earning" , "createdAt":{"$gte": start_date,"$lt": end_date}} , {"createdAt": 0 , "createdBy": 0 , "updatedAt": 0, "updatedBy": 0 , "type":0}).sort("createdAt", -1))
                    current_year_expenses_details = valuesEntity(db.earnings_expenses.find({"type": "expenses" , "createdAt":{"$gte": start_date,"$lt": end_date}} , {"createdAt": 0 , "createdBy": 0 , "updatedAt": 0, "updatedBy": 0 , "type":0}).sort("createdAt", -1))
                    for earning in current_year_earning_details:
                        current_year_earning_amount += earning['amount']
                    for expenses in current_year_expenses_details:
                        current_year_expenses_amount += expenses['amount']
                    data = {
                        'total_earning_amount':current_year_earning_amount,
                        'total_expenses_amount':current_year_expenses_amount,
                        'earing_details': current_year_earning_details
                    }
                    return onSuccess('Total earning',data)
            else:
                return badRequest('User not found.')
        else:   
            return unauthorisedRequest()

    def post(self, request):
        earning_type = ['donation' , 'registration_fee' , 'interest']
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]),"is_active":True, "is_admin" : True})
            if get_admin is not None:
                data = request.data
                if data['earning_type'] and data['earning_type'] in earning_type:
                    if data['date']:
                        if data['amount'] and data['amount']>0:
                            if data['online'] == True:
                                if data['transactionID'] and data['transactionID'] != '' and (' ' not in data['transactionID']):
                                    obj = {
                                        "earning_type": data['earning_type'],
                                        "date": data['date'],
                                        "amount": data['amount'],
                                        "online": data['online'],
                                        "transactionID": data['transactionID'],
                                        "type": "earning",
                                        "createdAt": datetime.datetime.now(),
                                        "updatedAt": "",
                                        "createdBy": get_admin['_id'],
                                        "updatedBy": "", 
                                    }
                                    db.earnings_expenses.insert_one(obj)
                                    return onSuccess('Earning added successfully.',1)
                                else:
                                    return badRequest('Invalid transactionID.')
                            else:
                                obj = {
                                    "earning_type": data['earning_type'],
                                    "date": data['date'],
                                    "amount": data['amount'],
                                    "online": False,
                                    "transactionID": "",
                                    "type": "earning",
                                    "createdAt": datetime.datetime.now(),
                                    "updatedAt": "",
                                    "createdBy": get_admin['_id'],
                                    "updatedBy": "", 
                                }
                                db.earnings_expenses.insert_one(obj)
                                return onSuccess('Earning added successfully.',1)
                        else:
                            return badRequest('Invalid amount.')
                    else:
                        badRequest('Invalid date.')
                else:
                    return badRequest('Invalid earning type.')
            else:
                return badRequest("Admin not found.")
        else:
            return unauthorisedRequest()
        
class AddExpensesAPI(APIView):
    def post(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]),"is_active":True, "is_admin" : True})
            if get_admin is not None:
                data = request.data
                if data['expenses_name']:
                    if data['date']:
                        if data['amount'] and data['amount']>0:
                            if data['online'] == True:
                                if data['transactionID'] and data['transactionID'] != '' and (' ' not in data['transactionID']):
                                    obj = {
                                        "expenses_name": data['expenses_name'],
                                        "date": data['date'],
                                        "amount": data['amount'],
                                        "online": data['online'],
                                        "transactionID": data['transactionID'],
                                        "type": "expenses",
                                        "createdAt": datetime.datetime.now(),
                                        "updatedAt": "",
                                        "createdBy": get_admin['_id'],
                                        "updatedBy": "", 
                                    }
                                    db.earnings_expenses.insert_one(obj)
                                    return onSuccess('Expenses added successfully.',1)
                                else:
                                    return badRequest('Invalid transactionID.')
                            else:
                                obj = {
                                    "expenses_name": data['expenses_name'],
                                    "date": data['date'],
                                    "amount": data['amount'],
                                    "online": False,
                                    "transactionID": "",
                                    "type": "expenses",
                                    "createdAt": datetime.datetime.now(),
                                    "updatedAt": "",
                                    "createdBy": get_admin['_id'],
                                    "updatedBy": "", 
                                }
                                db.earnings_expenses.insert_one(obj)
                                return onSuccess('Expenses added successfully.',1)
                        else:
                            return badRequest('Invalid amount.')
                    else:
                        badRequest('Invalid date.')
                else:
                    return badRequest('Invalid expenses.')
            else:
                return badRequest("Admin not found.")
        else:
            return unauthorisedRequest()    
        

class AddInterestAPI(APIView):
    
    def post(self, request):
        token = authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            get_admin = db.admin.find_one({"_id": ObjectId(token["_id"]),"is_active":True, "is_admin" : True})
            if get_admin is not None:
                data = request.data
                if data['fullname'] and data['total_amount'] and data['start_date'] and data['end_date'] and data['interest_percentage'] and data['interest_amount']:
                    if data['fullname'] != '' and all(chr.isalpha() or chr.isspace() for chr in data['fullname']):
                        if isinstance(data['total_amount'] , (int, float)):
                            if is_date_less_than_or_equal_today(data['start_date']):
                                if validate_date_formate(data['end_date']) and is_date_grater_than(data['start_date'] , data['end_date']):
                                    if isinstance(data['interest_percentage'] , float):
                                        if isinstance(data['interest_amount'] , (int, float)):
                                            obj = {
                                                "fullname": data['fullname'],
                                                "total_amount": data['total_amount'],
                                                "start_date": data['start_date'],
                                                "end_date": data['end_date'],
                                                "interest_percentage": data['interest_percentage'],
                                                "interest_amount": data['interest_amount'],
                                                "type": "interest",
                                                "createdAt": datetime.datetime.now(),
                                                "updatedAt": "",
                                                "createdBy": get_admin['_id'],
                                                "updatedBy": "", 
                                            }
                                            db.earnings_expenses.insert_one(obj)
                                            return onSuccess('Interest added successfully.',1)
                                        else:
                                            return badRequest('Invalid interest amount.')
                                    else:
                                        return badRequest('Invalid interest percentage.')
                                else:
                                    return badRequest('Invalid end date.')
                            else:
                                return badRequest('Invalid start date.')
                        else:
                            return badRequest('Invalid amount.')
                    else:
                        return badRequest('Invalid name.')
                else:
                    return badRequest('All the fields are necessary to fill.')                
            else:
                return badRequest("Admin not found.")
        else:
            return unauthorisedRequest()
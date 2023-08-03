import requests
from django.conf import settings

def send_otp(mobile_number , otp):
  admin = str(settings.SEND_OTP_URL) + mobile_number + '/' + otp
  payload={}
  headers = {}
  response = requests.request('GET' , admin , headers=headers , data=payload)
  if response.status_code == 200:
    return True
  return False

def verify_otp(mobile_number , otp):
  admin = str(settings.VERIFY_OTP_URL) + mobile_number + '/' + otp
  payload={}
  headers = {}
  response = requests.request('GET' , admin , headers=headers , data=payload)
  if response.status_code == 200:
    return True
  return False
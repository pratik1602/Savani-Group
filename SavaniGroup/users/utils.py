from django.core.mail import send_mail
from django.conf import settings

def send_verification_mail(email , subject , message):
  host_email = settings.EMAIL_HOST_USER
  send_mail(subject , message , host_email , [email])
  return True
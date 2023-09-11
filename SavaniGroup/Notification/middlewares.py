from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import jwt
from SavaniGroup.settings import SECRET_KEY
from bson.objectid import ObjectId
from rest_framework_simplejwt.tokens import TokenError

from core.db import db

JWT_ALGORITHM = "HS256"

@database_sync_to_async
def get_user(token):
    if token:
        payload = jwt.decode(token , SECRET_KEY , algorithms=JWT_ALGORITHM)
        if payload:
            get_admin = db.admin.find_one({"_id": ObjectId(payload["_id"]), "is_active":True, "is_admin" : True}, {"_id": 0,"password": 0,  "is_admin" : 0, "createdAt": 0,"updatedAt": 0,"updatedBy": 0})
        else:
            get_admin = AnonymousUser()
    else:
        get_admin = AnonymousUser()
    return get_admin
 
class TokenAuthMiddleWare:
    def __init__(self, app):
        self.app = app
 
    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"]
        query_params = query_string.decode()
        query_dict = parse_qs(query_params)
        try:
            token = query_dict["token"][0]
            user = await get_user(token)
            scope["user"] = user
        except TokenError:
            print('Token not found.')
            scope["user"] = AnonymousUser()
        return await self.app(scope, receive, send)
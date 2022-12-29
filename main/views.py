from curses.ascii import isdigit
from pydoc import doc
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *
from env import *
from utilities import *

# Create your views here.
class User(APIView):
    def get_user(self, page ,size, username=None):
        query = {"match_all":{}}
        if username is not None:
            query = {"match":{"username":username}}
        user_count = es.count(index="user_1", body={"query":query})["count"]
        pages = user_count // size
        if user_count % size != 0:
            pages += 1
        users = es.search(index="user_1", query=query, size=size, from_=(page-1)*size)["hits"]["hits"]
        return {"users":users, "total_record":user_count, "pages":pages}, HTTP_200_OK

    def get(self, request):
        data = request.GET
        username = data["username"] if "username" in data else None
        page = data["page"] if "page" in data else 1
        size = data["size"] if "size" in data else 20
        result = self.get_user(page=page, size=size, username=username)
        return Response(result[0], status=result[1])


    def register_user(self, email, password, username, phone_number):
        self.email = email
        self.password = password
        self.username = username
        self.phone_number = phone_number
        if es.count(index="user_1", body={"query":{"match":{"username.keyword":self.username}}})["count"] == 0:
            if es.count(index="user_1", body={"query":{"match":{"email.keyword":self.email}}})["count"] == 0:
                if es.count(index="user_1", body={"query":{"match":{"phone_number.keyword":self.phone_number}}})["count"] == 0:
                    if self.username not in ["admin", "user", "modir"]:
                        if "@gmail.com" in self.email:
                            if self.phone_number[:2] == "09" and self.phone_number[2:].isdigit() and len(self.phone_number) == 11:
                                if len(self.password) >= 8:
                                    self.data = {
                                        "email":self.email, 
                                        "password":hash_saz(self.password), 
                                        "username":self.username, 
                                        "phone_number": self.phone_number, 
                                        "status":"inactive"
                                    }
                                    es.index(index="user_1", id=self.username, document=self.data)
                                    return ({"message":"registered"}, HTTP_201_CREATED)
                                return ({"message":"password does not valid"}, HTTP_406_NOT_ACCEPTABLE)
                            return ({"message":"phone number does not valid"}, HTTP_406_NOT_ACCEPTABLE)
                        return ({"message":"email does not valid"}, HTTP_406_NOT_ACCEPTABLE)
                    return ({"message":"username does not valid"}, HTTP_406_NOT_ACCEPTABLE)
                return ({"message":"phone number is exists"}, HTTP_406_NOT_ACCEPTABLE)
            return ({"message":"email is exists"}, HTTP_406_NOT_ACCEPTABLE)
        return ({"message":"username is exists"}, HTTP_406_NOT_ACCEPTABLE)

    def post(self, request):
        data = request.data
        email = data["email"]
        username = data["username"]
        password = data["password"]
        phone_number = data["phone_number"]
        result = self.register_user(email=email, password=password, username=username, phone_number=phone_number)
        return Response(result[0], status=result[1])


class ActivePhoneNumver(APIView):
    def get(self, request):
        data = request.GET
        if check_code(data["username"], data["code"]):
            es.update(index="user_1", id=data["username"], doc={"status":"active"})
            return Response({"message":"user activate"}, status=HTTP_200_OK)
        return Response({"message":"code is wrong"}, status=HTTP_400_BAD_REQUEST)

    def post(self, request):
        username = request.data["username"]
        user_data = es.get(index="user_1", id=username)
        if user_data["_source"]["status"] == "inactive": 
            phone_number = user_data["_source"]["phone_number"]
            code = generate_code(username)
            if code:
                send_sms(phone_number, f"کد ارسالی برای شما عبارت است از :\n{code}")
                return Response({"message":"code sended"}, status=HTTP_200_OK)
            return Response({"message":"code is not expire"}, status=HTTP_403_FORBIDDEN)
        return Response({"message":"user is active"}, status=HTTP_403_FORBIDDEN)


class UpdateUser(APIView):
    def get(self, request):
        data = request.GET
        if check_code(data["username"], data["code"]):
            user_data = {}
            if "new_username" in data:
                user_data["username"] = data["new_username"]
            if "new_phone_number" in data:
                user_data["phone_number"] = data["new_phone_number"]
            if "new_email" in data:
                user_data["email"] = data["email"]
            if "new_password" in data:
                user_data["password"] = hash_saz(data["new_password"])
            es.update(index="user_1", id=data["username"], doc=user_data)
            return Response({"message":"user updated"}, status=HTTP_200_OK)
        return Response({"message":"code is wrong"}, status=HTTP_400_BAD_REQUEST)

    def post(self, request):
        username = request.data["username"]
        user_data = es.get(index="user_1", id=username)
        phone_number = user_data["_source"]["phone_number"]
        code = generate_code(username)
        if code:
            send_sms(phone_number, f"کد ارسالی برای شما عبارت است از :\n{code}")
            return Response({"message":"code sended"}, status=HTTP_200_OK)
        return Response({"message":"code is not expire"}, status=HTTP_403_FORBIDDEN)


class DeleteUser(APIView):
    def get(self, request):
        data = request.GET
        if check_code(data["username"], data["code"]):
            es.delete(index="user_1", id=data["username"])
            return Response({"message":"user deleted"}, status=HTTP_200_OK)
        return Response({"message":"code is wrong"}, status=HTTP_400_BAD_REQUEST)

    def post(self, request):
        username = request.data["username"]
        user_data = es.get(index="user_1", id=username)
        if user_data["_source"]["status"] == "inactive": 
            phone_number = user_data["_source"]["phone_number"]
            code = generate_code(username)
            if code:
                send_sms(phone_number, f"کد ارسالی برای شما عبارت است از :\n{code}")
                return Response({"message":"code sended"}, status=HTTP_200_OK)
            return Response({"message":"code is not expire"}, status=HTTP_403_FORBIDDEN)
        return Response({"message":"user is active"}, status=HTTP_403_FORBIDDEN)


class Login(APIView):
    def post(self, request):
        data = request.data
        user_data = es.search(index="user_1", query={"match":{"username.keyword":data["username"]}})["hits"]["hits"]
        if user_data:
            if user_data[0]["_source"]["password"] == hash_saz(data["password"]):
                access = jwt_generator(data["username"])
                return Response({"access":access}, status=HTTP_200_OK)
            return Response({"message":"password is wrong"}, status=HTTP_401_UNAUTHORIZED)
        return Response({"message":"user is not exists"}, status=HTTP_401_UNAUTHORIZED)


class AR_Model(APIView):
    def post(self, request):
        if Auth(jwt_checker(request.headers["Authorization"].split(" ")[1])):
            {"":request.data["noun"]}
            return Response({"message":"data added"}, status=HTTP_201_CREATED)
        return Response({"message":"user is not Autorize"}, status=HTTP_401_UNAUTHORIZED)
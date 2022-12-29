from django.test import TestCase
from time import sleep
from .views import *
import unittest

class UserTest(unittest.TestCase):
    def setUp(self):
        self.obj = User

    def test_get_user(self):
        self.page = 1
        self.size = 20
        data = self.obj.get_user(User, self.page, self.size)
        self.assertEqual(data[1], 200)
        user_count = es.count(index="user_1")["count"]
        self.assertEqual(data[0]["total_record"], user_count)
        self.assertEqual(data[0]["pages"], user_count // self.size if user_count % self.size == 0 else (user_count // self.size)+1)

    def test_register_user(self):
        self.email = "test@email.com"
        self.username = "testUser"
        self.phone_number = "09120000000"
        self.password = "12345678"
        data = self.obj.register_user(User, self.email, self.password, self.username, self.phone_number)
        self.assertEqual(data[1], 406)
        self.assertEqual(data[0]["message"], "email does not valid")

        self.email = "test@gmail.com"
        self.username = "admin"
        data = self.obj.register_user(User, self.email, self.password, self.username, self.phone_number)
        self.assertEqual(data[1], 406)
        self.assertEqual(data[0]["message"], "username does not valid")

        self.username = "testUser"
        self.phone_number = "0912000000"
        data = self.obj.register_user(User, self.email, self.password, self.username, self.phone_number)
        self.assertEqual(data[1], 406)
        self.assertEqual(data[0]["message"], "phone number does not valid")

        self.phone_number = "091200000T0"
        data = self.obj.register_user(User, self.email, self.password, self.username, self.phone_number)
        self.assertEqual(data[1], 406)
        self.assertEqual(data[0]["message"], "phone number does not valid")

        self.phone_number = "9120000000" 
        data = self.obj.register_user(User, self.email, self.password, self.username, self.phone_number)  
        self.assertEqual(data[1], 406)
        self.assertEqual(data[0]["message"], "phone number does not valid")

        self.phone_number = "09120000000"
        self.password = "1234567"
        data = self.obj.register_user(User, self.email, self.password, self.username, self.phone_number)
        self.assertEqual(data[1], 406)
        self.assertEqual(data[0]["message"], "password does not valid")

        self.password = "12345678"
        data = self.obj.register_user(User, self.email, self.password, self.username, self.phone_number)
        self.assertEqual(data[1], 201)
        self.assertEqual(data[0]["message"], "registered")
        sleep(1)
        es.delete(index="user_1", id=self.username)


def main():
    unittest.main()

if __name__ == "__main__":
    main()

from django.urls import *
from .views import *

app_name = "main"

urlpatterns = [
    path('user/', User.as_view()), 
    path('active_phone_numver', ActivePhoneNumver.as_view()), 
    path('update_user', UpdateUser.as_view()), 
    path('delete_user', DeleteUser.as_view()), 
    path('login', Login.as_view()), 
    path('ar_model', AR_Model.as_view()), 
]

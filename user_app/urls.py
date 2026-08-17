from django.urls import path
from user_app.views import Registration,login,logout

urlpatterns = [
    path('login/', login),
    path('logout/', logout),
    path('register/',Registration),
]
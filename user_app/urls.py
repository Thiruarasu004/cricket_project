from django.urls import path
from user_app.views import Registration, LoginView, LogoutView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", Registration.as_view(), name="register"),
]
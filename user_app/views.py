from rest_framework.views import APIView
from rest_framework.response import Response
from user_app.serializers import user_serializer
from django.contrib.auth.models import User
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from user_app import models
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class Registration(APIView):

    def post(self,request):
        serializer=user_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class login(APIView):

    def post(self,request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username,password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "message": "Login successful",
                    "token": token.key
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Invalid username or password"},
            status=status.HTTP_400_BAD_REQUEST
        )   

class logout(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self,request):
        request.user.auth_token.delete()
        return Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK
        )

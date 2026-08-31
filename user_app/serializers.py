from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    password_2 = serializers.CharField(style={'input_type':'password'},write_only=True)

    class Meta:
        model= User
        fields=["username","email","password","password_2"]
        extra_kwargs={'password':{'write_only':True}}

    def validate(self,data):
        if User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError("Username already exists.")
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("Email already exists.")
        if data["password"]!=data["password_2"]:
            raise serializers.ValidationError(
                "password_1 and password_2 are not same")
        return data

    def create(self,validated_data):
        validated_data.pop("password_2")
        return User.objects.create_user(
            **validated_data
        )


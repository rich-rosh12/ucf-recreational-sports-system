from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


# This serializer serves to format user profile data for the frontend client.
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "ucf_id",
            "role",
            "waiver_signed",
            "waiver_signed_at",
            "has_account_hold",
        ]
        read_only_fields = ["id", "role", "has_account_hold"]

    # This function serves to combine first and last name for display on the UI.
    def get_full_name(self, obj: User) -> str:
        return f"{obj.first_name} {obj.last_name}".strip()


# This serializer serves to embed RBAC role and UCF ID claims inside the JWT token.
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token["role"] = user.role
        token["ucf_id"] = user.ucf_id
        token["full_name"] = f"{user.first_name} {user.last_name}".strip()
        return token

    # This method serves to attach user details alongside the access and refresh tokens.
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
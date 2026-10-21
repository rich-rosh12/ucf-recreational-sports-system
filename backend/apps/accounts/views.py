from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import CustomTokenObtainPairSerializer, UserSerializer


# This view serves to add logic for login page and return JWT tokens.
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# This view serves to allow one-click demo login for Student, Worker, or Admin roles.
class QuickRoleSwitchView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        target_role = request.data.get("role", "STUDENT").upper()
        user = User.objects.filter(role=target_role).first()
        if not user:
            return Response(
                {"detail": f"No seeded user found for role {target_role}. Run seed_rwc_data first."},
                status=status.HTTP_404_NOT_FOUND,
            )
        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role
        refresh["ucf_id"] = user.ucf_id
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


# This view serves to fetch the currently authenticated user profile.
class CurrentUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# This view serves to record digital liability waiver signatures for students.
class SignWaiverView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.waiver_signed = True
        user.waiver_signed_at = timezone.now()
        user.save(update_fields=["waiver_signed", "waiver_signed_at"])
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
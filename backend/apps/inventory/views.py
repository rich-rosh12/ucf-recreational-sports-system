from rest_framework import viewsets, permissions
from apps.accounts.permissions import IsRecAdmin
from .models import EquipmentItem
from .serializers import EquipmentItemSerializer


# This viewset serves to provide read access to all users and write access strictly to Rec Admins.
class EquipmentItemViewSet(viewsets.ModelViewSet):
    queryset = EquipmentItem.objects.all().order_by("category", "name")
    serializer_class = EquipmentItemSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsRecAdmin()]

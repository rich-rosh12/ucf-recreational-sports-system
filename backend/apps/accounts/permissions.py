from rest_framework.permissions import BasePermission


# This class serves to grant access exclusively to authenticated students.
class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "STUDENT")


# This class serves to grant access to front desk rec workers and adminstrators.
class IsRecWorkerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ["WORKER", "ADMIN"]
        )


# This class serves to restrict sensitive inventory and role endpoints to rec adminstrators.
class IsRecAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "ADMIN")
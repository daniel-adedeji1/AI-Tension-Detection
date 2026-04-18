from .models import User
from rest_framework.authentication import BaseAuthentication # type: ignore

class CustomSessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if not request.session.get('is_authenticated'):
            return None

        employee_id = request.session.get('employee_id')

        if not employee_id:
            return None

        try:
            user = User.objects.get(employee_id=employee_id)
        except User.DoesNotExist:
            return None

        return (user, None)
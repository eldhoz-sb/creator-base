from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class OTPBackend(ModelBackend):
    def authenticate(self, request, otp=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(otp=otp)
        except UserModel.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None

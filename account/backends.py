from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()

        try:
            # Check if the user is a superuser
            user = User.objects.get(username=username, is_superuser=True)
        except User.DoesNotExist:
            try:
                # If not a superuser, check for a regular user
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        if user.check_password(password):
            return super().authenticate(request, username=username, password=password, **kwargs)

        return None
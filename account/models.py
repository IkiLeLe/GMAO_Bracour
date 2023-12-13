from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    badge_number = models.CharField(max_length=10, primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    position = models.CharField(max_length=50)

    # Spécifiez des noms de relation inverses uniques pour éviter les conflits
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",
        related_query_name="custom_user_group",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        related_query_name="custom_user_permission",
    )

    def __str__(self):
        return self.username

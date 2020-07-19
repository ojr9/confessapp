from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.urls import reverse


class User(AbstractUser):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, db_index=True)

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('user_view', args=[self.id],)

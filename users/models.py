from django.db import models
from django.contrib.auth.models import User #type: ignore

class AdminToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.token

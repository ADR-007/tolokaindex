from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True
        ordering = 'created_at',

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

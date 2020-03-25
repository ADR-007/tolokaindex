from django.db import models


class RawPost(models.Model):
    post_id = models.CharField(max_length=50, unique=True)
    title = models.TextField()
    row = models.TextField()
    registered_on = models.DateField()

from django.db import models


class LargeDeferredTask(models.Model):
    data = models.BinaryField()

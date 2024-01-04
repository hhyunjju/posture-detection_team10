from django.db import models

# Create your models here.
class CameraImage(models.Model):
    image = models.ImageField(upload_to='camera/')
    timestamp = models.DateTimeField(auto_now_add=True)

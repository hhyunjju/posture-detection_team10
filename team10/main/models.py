from django.db import models
from django.urls import reverse

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self) -> str:
        return self.name
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=50)
    
    def __str__(self) -> str:
        return self.user.name
    
class CameraImage(models.Model):
    image = models.ImageField(upload_to='camera/')
    timestamp = models.DateTimeField(auto_now_add=True)
    

from django import forms
from .models import CameraImage

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = CameraImage
        fields = ['image']
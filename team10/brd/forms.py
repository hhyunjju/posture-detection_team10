from django import forms
from .models import Post, Comment
    
#view-> post_create에서 사용
class PostModelForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'photo']
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

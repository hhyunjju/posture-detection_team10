from django.contrib import admin
from django.contrib.sessions.models import Session
from django.contrib import admin
from .models import Profile

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'expire_date']

admin.site.register(Profile)


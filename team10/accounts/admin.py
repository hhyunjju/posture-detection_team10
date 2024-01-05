from django.contrib import admin
from django.contrib.sessions.models import Session
from django.contrib import admin

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'expire_date']


from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create profile instances for existing social account users'

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            Profile.objects.get_or_create(
                user=user,
                defaults={'email': user.email}  # 기본값 설정
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created profile for {user.username}'))

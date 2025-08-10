from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Create or update a Django superuser from environment variables"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("ADMIN_USERNAME", "admin")
        email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        password = os.getenv("ADMIN_PASSWORD", "admin")

        user, created = User.objects.get_or_create(username=username, defaults={
            "email": email,
            "is_staff": True,
            "is_superuser": True,
        })

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created"))
        else:
            # Ensure superuser flags and reset password to given one
            updated = False
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                updated = True
            if password:
                user.set_password(password)
                updated = True
            if email and user.email != email:
                user.email = email
                updated = True
            if updated:
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' updated"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already up to date"))

        return None 
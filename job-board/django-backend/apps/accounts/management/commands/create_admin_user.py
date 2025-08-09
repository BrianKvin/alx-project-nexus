import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

class Command(BaseCommand):
    help = 'Creates a superuser with default credentials if it doesn\'t exist'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get admin credentials from environment variables with defaults
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin')
        
        try:
            # Try to get the admin user
            admin = User.objects.get(username=admin_username)
            self.stdout.write(
                self.style.SUCCESS(f'Admin user {admin_username} exists. Updating...')
            )
            admin.set_password(admin_password)
            admin.email = admin_email
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            self.stdout.write(
                self.style.SUCCESS(f'Admin {admin_username} updated successfully')
            )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.SUCCESS(f'Creating admin user {admin_username}...')
            )
            User.objects.create_superuser(admin_username, admin_email, admin_password)
            self.stdout.write(
                self.style.SUCCESS(f'Admin user {admin_username} created successfully')
            )
                
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Error managing admin user: {str(e)}')
            )
            raise e

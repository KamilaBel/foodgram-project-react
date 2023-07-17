import os

from django.contrib.auth.hashers import make_password
from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = ''' Create initial data '''

    def create_users(self):
        obj, created = User.objects.get_or_create(
            username='admin', email='admin@test.com',
            defaults={
                'first_name': 'Иван',
                'last_name': 'Сидоров',
                'password': make_password(
                    os.environ.get('ADMIN_TEST_PASSWORD', 'testmeplease')
                ),
                'is_staff': True,
                'is_superuser': True,
            })
        if created:
            print(f'Created admin user: {obj}')

    def handle(self, *args, **options):
        self.create_users()

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Cria o superusuario padrao caso nao exista"

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@picklepesp.com", "admin123")
            self.stdout.write(self.style.SUCCESS("Superusuario 'admin' criado com senha 'admin123'"))
        else:
            self.stdout.write("Superusuario 'admin' ja existe")

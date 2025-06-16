from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Cria usuários de teste para cada nível de acesso'

    def handle(self, *args, **kwargs):
        # Criar usuário administrador
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@teste.com',
            password='admin123',
            user_type=User.UserType.ADMIN,
            is_staff=True,
            is_superuser=True
        )
        self.stdout.write(self.style.SUCCESS('Usuário administrador criado com sucesso!'))

        # Criar usuário gestor
        manager_user = User.objects.create_user(
            username='gestor',
            email='gestor@teste.com',
            password='gestor123',
            user_type=User.UserType.MANAGER
        )
        self.stdout.write(self.style.SUCCESS('Usuário gestor criado com sucesso!'))

        # Criar usuário comum
        common_user = User.objects.create_user(
            username='usuario',
            email='usuario@teste.com',
            password='usuario123',
            user_type=User.UserType.COMMON
        )
        self.stdout.write(self.style.SUCCESS('Usuário comum criado com sucesso!')) 
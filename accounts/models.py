from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

# --- Modelo de usuário customizado ---
class CustomUser(AbstractUser):
    # Definimos os tipos de usuário
    ROLES = (
        ('colaborador', 'Colaborador'),
        ('tecnico', 'Técnico'),
        ('admin', 'Administrador'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='colaborador')

    # Tornar o e-mail obrigatório e único
    email = models.EmailField(unique=True)

    # Definir e-mail como campo principal para login
    USERNAME_FIELD = 'email'  # campo que será usado para autenticação
    REQUIRED_FIELDS = ['username']  # campos obrigatórios além do e-mail

    def __str__(self):
        return f"{self.username} ({self.role})"
class Ticket(models.Model):
    STATUS_CHOICES = (
        ('ativo', 'Ativo'),
        ('concluido', 'Concluído'),
    )

    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ativo')
    colaborador = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='chamados_abertos'
    )  # quem abriu o chamado
    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='chamados_atendidos'
    )  # técnico responsável (opcional)
    data_criacao = models.DateTimeField(default=timezone.now)
    data_fechamento = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.titulo} ({self.status})"
    from django.db import models
from django.conf import settings

class Chamado(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('em_andamento', 'Em andamento'),
        ('concluido', 'Concluído'),
    ]

    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

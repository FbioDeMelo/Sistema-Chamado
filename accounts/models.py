from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator

# --- Validador personalizado ---
nome_usuario_validator = RegexValidator(
    regex=r'^[\w\sáàâãäéèêëíìîïóòôõöúùûüçÇÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜ-]+$',
    message="O nome de usuário pode conter letras, espaços, acentos e traços."
)

# --- Modelo de usuário customizado ---
class CustomUser(AbstractUser):
    ROLES = (
        ('colaborador', 'Colaborador'),
        ('tecnico', 'Técnico'),
        ('admin', 'Administrador'),
    )

    role = models.CharField(max_length=20, choices=ROLES, default='colaborador')

    email = models.EmailField(unique=True)

    # Campo username personalizado
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[nome_usuario_validator],
        help_text="Pode conter letras, espaços e acentos.",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

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
class Mensagem(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='mensagens')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.autor.username} - {self.ticket.titulo} - {self.data_envio.strftime('%d/%m %H:%M')}"
    
    from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Notificacao(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificacoes')
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField(blank=True)
    target_url = models.CharField(max_length=300, blank=True)  # ex: /chamados/1/
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titulo} -> {self.recipient}"

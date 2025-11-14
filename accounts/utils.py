# accounts/utils.py
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Notificacao, Ticket, Mensagem

User = get_user_model()

def notify_new_ticket(ticket):
    """
    Notifica todos os técnicos e admins que um novo ticket foi criado.
    """
    titulo = f"Novo chamado aberto: {ticket.titulo} (ID #{ticket.id})"
    mensagem = f"Um novo chamado foi aberto: {ticket.titulo}."
    target = f"/chamados/{ticket.id}/"  # ajuste se sua rota for outra

    # técnicos + admin
    tecnicos = User.objects.filter(role__in=['tecnico', 'admin'])
    for user in tecnicos:
        Notificacao.objects.create(
            recipient=user,
            titulo=titulo,
            mensagem=mensagem,
            target_url=target
        )

def notify_ticket_closed(ticket, tecnico_user):
    """
    Notifica o colaborador dono que o ticket foi fechado e cria
    uma mensagem automática no chat (Mensagem).
    """
    # 1) criar mensagem automática no chat
    texto = f"Chamado finalizado pelo técnico {tecnico_user.username}."
    Mensagem.objects.create(ticket=ticket, autor=tecnico_user, texto=texto)

    # 2) notificar o colaborador dono
    titulo = f"Seu chamado {ticket.titulo} (ID #{ticket.id}) foi concluído."
    mensagem = f"O chamado '{ticket.titulo}' foi concluído pelo técnico {tecnico_user.username}."
    target = f"/chamados/{ticket.id}/"

    Notificacao.objects.create(
        recipient=ticket.colaborador,
        titulo=titulo,
        mensagem=mensagem,
        target_url=target
    )

    # 3) (opcional) notificar todos os técnicos/admins também (se quiser)
    tecnicos = User.objects.filter(role__in=['tecnico', 'admin'])
    for user in tecnicos:
        Notificacao.objects.create(
            recipient=user,
            titulo=f"Chamado concluído: {ticket.titulo} (ID #{ticket.id})",
            mensagem=mensagem,
            target_url=target
        )

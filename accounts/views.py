from django.shortcuts import render, redirect  # render = mostra o HTML; redirect = redireciona pra outra página
from django.contrib.auth import authenticate, login, logout  # funções prontas do Django para login/logout
from django.contrib import messages  # permite exibir mensagens de erro ou sucesso
from django.core.mail import send_mail

# --- VIEW DE LOGIN ---
def login_view(request):
    # Se o usuário já estiver logado, vai direto pra home
    if request.user.is_authenticated:
        return redirect('home')

    # Processa o formulário apenas se for POST
    if request.method == 'POST':
        email = request.POST.get('email')      # pega o e-mail digitado
        password = request.POST.get('password') # pega a senha digitada
        user = authenticate(request, email=email, password=password)  # autentica pelo e-mail

        if user is not None:
          login(request, user)
          return redirect('index')  # envia pro index geral
        else:
            messages.error(request, 'E-mail ou senha incorretos.')

    # Renderiza o template de login se for GET ou se houver erro
    return render(request, 'accounts/login.html')



# --- VIEW DA HOME ---
def home_view(request):
    if not request.user.is_authenticated:  # se não estiver logado
        return redirect('login')  # volta pra tela de login
    return render(request, 'accounts/home.html')  # mostra a página inicial


# --- VIEW DE LOGOUT ---
def logout_view(request):
    logout(request)
    return redirect('login')
from django.shortcuts import render, redirect
from .models import Ticket
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator

# --- Tela principal de chamados ---
from django.core.mail import send_mail
from django.conf import settings
from .utils import notify_new_ticket, notify_ticket_closed
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Ticket

@login_required
def chamados_colaborador(request):
    if request.user.role not in ['colaborador', 'admin']:
        return redirect('index')

    chamados_list = Ticket.objects.filter(colaborador=request.user)
    paginator = Paginator(chamados_list, 5)  # 5 chamados por página
    page_number = request.GET.get('page')
    chamados = paginator.get_page(page_number)

    if request.method == 'POST':
        ativos = chamados_list.filter(status='ativo').count()
        if ativos >= 3:
            messages.error(request, "Você já possui 3 chamados ativos.")
        else:
            titulo = request.POST.get('titulo')
            descricao = request.POST.get('descricao')

            # Cria o ticket
            novo_ticket = Ticket.objects.create(
                titulo=titulo,
                descricao=descricao,
                colaborador=request.user
            )

            # --- Envio de e-mail automático ---
            assunto = f"Novo chamado aberto: {novo_ticket.titulo}"
            mensagem = (
                f"Olá {request.user.username},\n\n"
                f"Seu chamado foi aberto com sucesso!\n\n"
                f"Detalhes do chamado:\n"
                f"Título: {novo_ticket.titulo}\n"
                f"Descrição: {novo_ticket.descricao}\n"
                f"Status atual: {novo_ticket.status}\n\n"
                f"Em breve, um técnico entrará em contato.\n\n"
                f"Atenciosamente,\nEquipe de Suporte"
            )
            send_mail(
                assunto,
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )

            # --- Notificação em tempo real (sino) ---
            notify_new_ticket(novo_ticket)

            messages.success(request, "Chamado criado com sucesso! E-mail e notificação enviados.")
            return redirect('chamados_colaborador')

    return render(request, 'accounts/chamados_colaborador.html', {'chamados': chamados})

# --- Tela de chamados para técnico ---
@login_required
def chamados_tecnico(request):
    if request.user.role != 'tecnico':
        return redirect('home')

    chamados_ativos_list = Ticket.objects.filter(status='ativo')
    chamados_concluidos_list = Ticket.objects.filter(status='concluido')

    paginator_ativos = Paginator(chamados_ativos_list, 5)
    paginator_concluidos = Paginator(chamados_concluidos_list, 5)

    page_number_ativos = request.GET.get('page_ativos')
    page_number_concluidos = request.GET.get('page_concluidos')

    chamados_ativos = paginator_ativos.get_page(page_number_ativos)
    chamados_concluidos = paginator_concluidos.get_page(page_number_concluidos)

    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        ticket = get_object_or_404(Ticket, id=ticket_id)
        ticket.status = 'concluido'
        ticket.data_fechamento = timezone.now()
        ticket.tecnico = request.user
        ticket.save()

        # --- Envio de e-mail automático ao colaborador ---
        assunto = f"Chamado concluído: {ticket.titulo}"
        mensagem = (
            f"Olá {ticket.colaborador.username},\n\n"
            f"Seu chamado foi concluído com sucesso!\n\n"
            f"Detalhes do chamado:\n"
            f"Título: {ticket.titulo}\n"
            f"Concluído por: {request.user.username}\n"
            f"Data de fechamento: {ticket.data_fechamento.strftime('%d/%m/%Y %H:%M')}\n\n"
            f"Agradecemos por utilizar nosso suporte.\n"
            f"Atenciosamente,\nEquipe de Suporte"
        )
        send_mail(
            assunto,
            mensagem,
            settings.DEFAULT_FROM_EMAIL,
            [ticket.colaborador.email],
            fail_silently=False,
        )

        # --- Notificação em tempo real para o colaborador e outros técnicos ---
        notify_ticket_closed(ticket, request.user)

        messages.success(request, "Chamado concluído! E-mail e notificação enviados.")
        return redirect('chamados_tecnico')

    return render(request, 'accounts/chamados_tecnico.html', {
        'chamados_ativos': chamados_ativos,
        'chamados_concluidos': chamados_concluidos
    })
# --- Tela para admin (visualizar tudo) ---
@login_required
def chamados_admin(request):
    if request.user.role != 'admin':
        return redirect('index')

    todos_chamados_list = Ticket.objects.all()
    paginator = Paginator(todos_chamados_list, 12)  # 10 chamados por página
    page_number = request.GET.get('page')
    todos_chamados = paginator.get_page(page_number)

    return render(request, 'accounts/chamados_admin.html', {'todos_chamados': todos_chamados})

from django.shortcuts import redirect

@login_required
def home_redirect(request):
    """
    Redireciona o usuário para a tela correta dependendo do tipo de usuário
    """
    if request.user.role == 'colaborador':
        return redirect('chamados_colaborador')
    elif request.user.role == 'tecnico':
        return redirect('chamados_tecnico')
    elif request.user.role == 'admin':
        return redirect('chamados_admin')
    else:
        # Caso role não esteja definido, desloga o usuário
        return redirect('logout')
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import AdminUserCreationForm
from django.contrib import messages

@login_required
def criar_usuario(request):
    # Só admin pode acessar
    if request.user.role != 'admin':
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect('home')

    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Se for colaborador, salva o setor
            if user.role == 'colaborador':
                user.setor = form.cleaned_data['setor']
            user.save()
            messages.success(request, f"Usuário {user.username} criado com sucesso!")
            return redirect('criar_usuario')
    else:
        form = AdminUserCreationForm()

    return render(request, 'accounts/criar_usuario.html', {'form': form})
@login_required
def index_geral(request):
    """
    Página inicial geral: mostra cards conforme o tipo de usuário
    """
    cards = []

    if request.user.role == 'colaborador':
        cards = [
            {
                'titulo': 'Abrir Chamado',
                'descricao': 'Crie um novo chamado de suporte.',
                'url': 'chamados_colaborador'
            },
            {
                'titulo': 'Meus Chamados',
                'descricao': 'Acompanhe o status dos seus chamados.',
                'url': 'chamados_colaborador'
            },
        ]

    elif request.user.role == 'tecnico':
        cards = [
            {
                'titulo': 'Chamados Atribuídos',
                'descricao': 'Gerencie e conclua chamados em aberto.',
                'url': 'chamados_tecnico'
            },
        ]

    elif request.user.role == 'admin':
        cards = [
            {
                'titulo': 'Todos os Chamados',
                'descricao': 'Visualize todos os chamados do sistema.',
                'url': 'chamados_admin'
            },
            {
                'titulo': 'Criar Usuário',
                'descricao': 'Adicione novos usuários e defina seus papéis.',
                'url': 'criar_usuario'
            },
            {
                'titulo': 'Gerenciar Usuários',
                'descricao': 'Visualize, edite ou remova contas de usuários.',
                'url': 'gerenciar_usuarios'  # <-- nome da URL que criamos
            },

                    {
                'titulo': 'Abrir Chamado',
                'descricao': 'Crie um novo chamado de suporte.',
                'url': 'chamados_colaborador'
            },
        ]

    else:
        messages.error(request, "Função de usuário não reconhecida.")
        return redirect('logout')

    return render(request, 'accounts/index.html', {'cards': cards})
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()

@login_required
def gerenciar_usuarios(request):
    # Apenas o admin pode acessar
    if request.user.role != 'admin':
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect('index')

    usuarios = User.objects.all()

    # Se o admin enviou o formulário de edição
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        novo_nome = request.POST.get('username')
        novo_email = request.POST.get('email')
        nova_senha = request.POST.get('password')

        try:
            usuario = User.objects.get(id=user_id)
            usuario.username = novo_nome
            usuario.email = novo_email
            if nova_senha:
                usuario.set_password(nova_senha)
            usuario.save()
            messages.success(request, f"Usuário {usuario.username} atualizado com sucesso!")
            return redirect('gerenciar_usuarios')
        except User.DoesNotExist:
            messages.error(request, "Usuário não encontrado.")

    return render(request, 'accounts/gerenciar_usuarios.html', {'usuarios': usuarios})
# accounts/views.py
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import Ticket

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(is_admin)
def graficos_tickets(request):
    """
    Exibe um gráfico intuitivo de tickets abertos e concluídos.
    Apenas administradores podem acessar.
    """
    hoje = timezone.now().date()
    dias = int(request.GET.get('dias', 30))
    inicio = hoje - timedelta(days=dias)

    tickets = Ticket.objects.filter(data_criacao__date__gte=inicio)

    datas = []
    abertos = []
    concluidos = []

    for i in range(dias + 1):
      dia = inicio + timedelta(days=i)
      datas.append(dia.strftime('%d/%m'))
      abertos.append(tickets.filter(data_criacao__date=dia).count())
      concluidos.append(tickets.filter(status='concluido', data_fechamento__date=dia).count())

    contexto = {
        'titulo': 'Gráficos de Tickets',
        'descricao': 'Acompanhe a evolução dos chamados abertos e concluídos.',
        'datas': datas,
        'abertos': abertos,
        'concluidos': concluidos,
    }

    return render(request, 'accounts/graficos_tickets.html', contexto)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Ticket, Mensagem
from django.shortcuts import get_object_or_404, render

@login_required
def chat_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Apenas admin, colaborador dono ou técnico podem acessar
    if not (request.user.role == 'tecnico' or request.user == ticket.colaborador or request.user.role == 'admin'):
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    # Bloquear colaborador se o ticket estiver concluído
    if request.method == 'POST':
        if ticket.status == 'concluido' and request.user.role == 'colaborador':
            return JsonResponse({'erro': 'Não é possível enviar mensagens em chamado concluído.'}, status=403)

        texto = request.POST.get('texto')
        if texto:
            Mensagem.objects.create(ticket=ticket, autor=request.user, texto=texto)
            return JsonResponse({'sucesso': True})

    # Para GET ou atualização
    mensagens = ticket.mensagens.order_by('data_envio').values(
        'autor__username', 'texto', 'data_envio'
    )
    mensagens_list = [
        {
            'autor': m['autor__username'],
            'texto': m['texto'],
            'data_envio': m['data_envio'].strftime('%d/%m %H:%M')
        } for m in mensagens
    ]
    return JsonResponse({'mensagens': mensagens_list, 'status': ticket.status})
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notificacao

@login_required
def verificar_notificacoes(request):
    """
    Retorna { unread_count: N }
    """
    unread = Notificacao.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread})

@login_required
def listar_notificacoes(request):
    """
    Retorna JSON com as notificações do usuário (últimas 50).
    """
    notifs = Notificacao.objects.filter(recipient=request.user).order_by('-created_at')[:50]
    data = []
    for n in notifs:
        data.append({
            'id': n.id,
            'titulo': n.titulo,
            'mensagem': n.mensagem,
            'target_url': n.target_url,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%d/%m %H:%M'),
        })
    return JsonResponse({'notificacoes': data})

@login_required
def marcar_como_lida(request, notif_id):
    """
    Marca notificação como lida e retorna redirect_url em JSON.
    """
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método inválido'}, status=400)

    try:
        n = Notificacao.objects.get(id=notif_id, recipient=request.user)
    except Notificacao.DoesNotExist:
        return JsonResponse({'erro': 'Notificação não encontrada'}, status=404)

    n.is_read = True
    n.save()
    return JsonResponse({'sucesso': True, 'target_url': n.target_url})



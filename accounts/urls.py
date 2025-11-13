from django.urls import path
from django.shortcuts import redirect
from . import views  # importa as funções que criaremos em views.py

urlpatterns = [
    # --- Redirecionamento da raiz ---
    path('', lambda request: redirect('index')),  # evita erro 404 na raiz

    # --- Login / Logout ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- Chamados ---
    path('chamados/colaborador/', views.chamados_colaborador, name='chamados_colaborador'),
    path('chamados/tecnico/', views.chamados_tecnico, name='chamados_tecnico'),
    path('chamados/admin/', views.chamados_admin, name='chamados_admin'),

    # --- Usuários ---
    path('criar_usuario/', views.criar_usuario, name='criar_usuario'),
    path('gerenciar-usuarios/', views.gerenciar_usuarios, name='gerenciar_usuarios'),

    # --- Index geral ---
    path('index/', views.index_geral, name='index'),

    # --- Dashboard Admin ---
path('graficos-tickets/', views.graficos_tickets, name='graficos_tickets'),
    path('chat/<int:ticket_id>/', views.chat_ticket, name='chat_ticket'),

]

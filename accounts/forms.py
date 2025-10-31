from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class AdminUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('colaborador', 'Colaborador'),
        ('tecnico', 'Técnico'),
        ('admin', 'Admin'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Tipo de usuário')
    setor = forms.CharField(max_length=50, required=False, label='Setor (apenas para colaboradores)')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'setor', 'password1', 'password2')

    # --- validação customizada ---
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        setor = cleaned_data.get('setor')

        # Se for colaborador, setor é obrigatório
        if role == 'colaborador' and not setor:
            self.add_error('setor', 'O setor é obrigatório para colaboradores.')

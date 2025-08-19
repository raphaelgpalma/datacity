from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    nome = forms.CharField(max_length=100, required=True, label='Nome Completo')
    email = forms.EmailField(required=True)
    cpf = forms.CharField(max_length=14, required=True, label='CPF', 
                         help_text='Formato: 000.000.000-00')
    cidade = forms.CharField(max_length=100, required=True)
    categoria = forms.ChoiceField(
        choices=User.CategoriaChoices.choices,
        required=True,
        label='Categoria'
    )
    user_type = forms.ChoiceField(choices=User.UserType.choices, required=True, label='Tipo de Usuário')

    class Meta:
        model = User
        fields = ['username', 'nome', 'email', 'cpf', 'cidade', 'categoria', 'password1', 'password2', 'user_type']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, label='Email ou Usuário')
    password = forms.CharField(widget=forms.PasswordInput, label='Senha')
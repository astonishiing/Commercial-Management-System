"""
Formulário customizado de recuperação de senha.

O PasswordResetForm padrão do Django busca usuários pelo campo `email`
do model de usuário, mas o nosso model Usuario tem `username` como campo
principal de identificação (USERNAME_FIELD = 'username').

Este form:
  1. Pede o USERNAME no formulário (não o e-mail).
  2. Busca o usuário pelo username.
  3. Envia o link de recuperação para o e-mail cadastrado nesse usuário.

Se o usuário não tiver e-mail cadastrado, nenhum e-mail é enviado
(mas por segurança a tela de "e-mail enviado" é exibida do mesmo jeito,
para não revelar quais usuários existem no sistema).
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

Usuario = get_user_model()


class PasswordResetForm(DjangoPasswordResetForm):
    """
    Substitui o campo `email` por `username` (rotulado como
    "Usuário") e localiza o e-mail a partir do usuário encontrado.
    """

    # Sobrescreve o campo 'email' do form padrão, mas mantém o
    # mesmo nome de campo para reaproveitar o template existente
    # ({{ form.email }} continua funcionando).
    email = forms.CharField(
        label='Usuário',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu usuário',
            'autocomplete': 'username',
        })
    )

    def get_users(self, username):
        """Retorna os usuários ativos que correspondem ao username informado."""
        try:
            user = Usuario.objects.get(username__iexact=username, is_active=True)
        except Usuario.DoesNotExist:
            return []

        # Só retorna o usuário se ele tiver um e-mail e senha utilizável
        if user.email and user.has_usable_password():
            return [user]
        return []

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Mesma lógica do form padrão do Django, mas usando o
        username informado (campo 'email' deste form) para localizar
        o(s) usuário(s) via get_users().
        """
        username = self.cleaned_data['email']
        for user in self.get_users(username):
            user_email = user.email
            if not domain_override:
                from django.contrib.sites.shortcuts import get_current_site
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override

            context = {
                'email': user_email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }

            subject = render_to_string(subject_template_name, context)
            subject = ''.join(subject.splitlines())  # remove quebras de linha
            body = render_to_string(email_template_name, context)

            email_message = EmailMultiAlternatives(subject, body, from_email, [user_email])
            email_message.send()

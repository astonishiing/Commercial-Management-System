# urls_web.py — Entrega 3: login/logout + recuperação de senha por e-mail
from django.urls import path
from django.contrib.auth import views as auth_views
from .views_web import LoginWebView, LogoutWebView
from .forms import PasswordResetForm

urlpatterns = [
    path('login/',  LoginWebView.as_view(),  name='login'),
    path('logout/', LogoutWebView.as_view(), name='logout'),

    # ── Recuperação de senha por e-mail (Entrega 3) ───────────────────
    # Usa um form customizado (PasswordResetForm) que busca o usuário
    # pelo USERNAME em vez de e-mail, já que o model Usuario é customizado.
    path('senha/recuperar/',
         auth_views.PasswordResetView.as_view(
             form_class=PasswordResetForm,
             template_name='auth/senha_recuperar.html',
             email_template_name='auth/senha_recuperar_email.txt',
             subject_template_name='auth/senha_recuperar_assunto.txt',
             success_url='/auth/senha/enviado/',
         ), name='password_reset'),

    path('senha/enviado/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/senha_enviado.html',
         ), name='password_reset_done'),

    path('senha/redefinir/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='auth/senha_redefinir.html',
             success_url='/auth/senha/concluido/',
         ), name='password_reset_confirm'),

    path('senha/concluido/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='auth/senha_concluido.html',
         ), name='password_reset_complete'),
]

"""
Views da API de autenticação.
POST /api/auth/login   → retorna access + refresh token (JWT)
POST /api/auth/refresh → renova o access token
POST /api/auth/register → cria novo usuário (somente ADMIN)
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import RegistroUsuarioSerializer, UsuarioSerializer
from .models import Usuario


class LoginView(TokenObtainPairView):
    """POST /api/auth/login — retorna JWT com informações do usuário."""
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Inclui dados do usuário junto com o token
            user = Usuario.objects.get(username=request.data['username'])
            response.data['usuario'] = UsuarioSerializer(user).data
        return response


class RegistroView(APIView):
    """POST /api/auth/register — cria usuário (somente ADMIN)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.user.is_admin:
            return Response(
                {'erro': 'Apenas administradores podem criar usuários.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = RegistroUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'mensagem': 'Usuário criado com sucesso.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeuPerfilView(APIView):
    """GET /api/auth/me — retorna dados do usuário autenticado."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)

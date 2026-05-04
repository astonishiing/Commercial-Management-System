"""
API REST de Clientes — usa o ClienteService da camada de aplicação.
A view não conhece regras de negócio — ela só converte HTTP ↔ Service.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from application.services import ClienteService
from .serializers import ClienteSerializer
from .models import Cliente
from apps.usuarios.permissions import IsAdminOrReadOnly

_svc = ClienteService()


class ClienteListCreateAPIView(APIView):
    # GET: qualquer autenticado | POST: somente ADMIN
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        """GET /api/clientes/ — lista todos os clientes."""
        clientes = Cliente.objects.all().order_by('nome')
        return Response(ClienteSerializer(clientes, many=True).data)

    def post(self, request):
        """POST /api/clientes/ — cadastra novo cliente (ADMIN)."""
        try:
            cliente = _svc.cadastrar(
                nome=request.data.get('nome', ''),
                cpf=request.data.get('cpf', ''),
                email=request.data.get('email', ''),
                telefone=request.data.get('telefone', ''),
                endereco=request.data.get('endereco', ''),
            )
            return Response(
                {'mensagem': 'Cliente cadastrado com sucesso.', 'id': cliente.id},
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ClienteDetailAPIView(APIView):
    # GET: qualquer autenticado | PUT/DELETE: somente ADMIN
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        """GET /api/clientes/{id}/ — detalhe do cliente."""
        try:
            obj = Cliente.objects.get(pk=pk)
            return Response(ClienteSerializer(obj).data)
        except Cliente.DoesNotExist:
            return Response({'erro': 'Cliente não encontrado.'}, status=404)

    def put(self, request, pk):
        """PUT /api/clientes/{id}/ — atualiza cliente (ADMIN)."""
        try:
            _svc.atualizar(pk, **{
                k: v for k, v in request.data.items()
                if k in ['nome', 'cpf', 'email', 'telefone', 'endereco']
            })
            return Response({'mensagem': 'Cliente atualizado com sucesso.'})
        except ValueError as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """DELETE /api/clientes/{id}/ — remove cliente (ADMIN)."""
        try:
            _svc.remover(pk)
            return Response({'mensagem': 'Cliente removido com sucesso.'})
        except ValueError as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)

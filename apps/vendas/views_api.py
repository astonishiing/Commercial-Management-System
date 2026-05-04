"""
API REST de Vendas.
GET  /api/vendas/          — lista todas as vendas
GET  /api/vendas/{id}/     — detalhe de uma venda
POST /api/vendas/          — registra nova venda
POST /api/vendas/periodo/  — vendas por período (filtro)
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from application.services import VendaService
from .serializers import VendaSerializer, VendaCreateSerializer
from .models import Venda

_svc = VendaService()


class VendaListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        vendas = Venda.objects.select_related('cliente', 'usuario').all()
        return Response(VendaSerializer(vendas, many=True).data)

    def post(self, request):
        """POST /api/vendas/ — registra nova venda."""
        s = VendaCreateSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            venda = _svc.registrar(
                cliente_id=s.validated_data['cliente_id'],
                usuario_id=request.user.id,
                itens_data=s.validated_data['itens'],
            )
            return Response(
                {'mensagem': 'Venda registrada com sucesso.', 'id': venda.id,
                 'total': float(venda.calcular_total())},
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VendaDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            obj = Venda.objects.select_related('cliente', 'usuario').get(pk=pk)
            return Response(VendaSerializer(obj).data)
        except Venda.DoesNotExist:
            return Response({'erro': 'Venda não encontrada.'}, status=404)


class VendaPorPeriodoAPIView(APIView):
    """POST /api/vendas/periodo/ — filtra vendas por período."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data_inicio = request.data.get('data_inicio')
        data_fim    = request.data.get('data_fim')
        if not data_inicio or not data_fim:
            return Response({'erro': 'Informe data_inicio e data_fim (YYYY-MM-DD).'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            from datetime import datetime
            di = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            df = datetime.strptime(data_fim, '%Y-%m-%d').date()
            vendas = Venda.objects.filter(
                data__date__gte=di, data__date__lte=df
            ).select_related('cliente', 'usuario')
            return Response(VendaSerializer(vendas, many=True).data)
        except ValueError as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)

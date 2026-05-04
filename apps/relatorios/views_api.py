"""
API REST de Relatórios.
A view apenas chama RelatorioService.gerar(tipo, **kwargs).
A escolha da estratégia certa é feita internamente pela Factory.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from application.services import RelatorioService

_svc = RelatorioService()


class RelatorioPorClienteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, cliente_id):
        try:
            dados = _svc.gerar('cliente', cliente_id=cliente_id)
            return Response(dados)
        except ValueError as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RelatorioPorPeriodoAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data_inicio = request.query_params.get('inicio')
        data_fim    = request.query_params.get('fim')
        try:
            dados = _svc.gerar('periodo', data_inicio=data_inicio, data_fim=data_fim)
            return Response(dados)
        except ValueError as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RelatorioPorProdutoAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            dados = _svc.gerar('produto')
            return Response(dados)
        except ValueError as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)

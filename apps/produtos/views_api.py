from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from application.services import ProdutoService
from .serializers import ProdutoSerializer
from .models import Produto
from apps.usuarios.permissions import IsAdminOrReadOnly

_svc = ProdutoService()


class ProdutoListCreateAPIView(APIView):
    # GET: qualquer autenticado | POST: somente ADMIN
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        produtos = Produto.objects.all().order_by('nome')
        return Response(ProdutoSerializer(produtos, many=True).data)

    def post(self, request):
        try:
            from decimal import Decimal
            p = _svc.cadastrar(
                nome=request.data.get('nome', ''),
                descricao=request.data.get('descricao', ''),
                preco=Decimal(str(request.data.get('preco', '0'))),
                quantidade_estoque=int(request.data.get('quantidade_estoque', 0)),
            )
            return Response({'mensagem': 'Produto cadastrado.', 'id': p.id}, status=201)
        except (ValueError, Exception) as e:
            return Response({'erro': str(e)}, status=400)


class ProdutoDetailAPIView(APIView):
    # GET: qualquer autenticado | PUT/DELETE: somente ADMIN
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        try:
            return Response(ProdutoSerializer(Produto.objects.get(pk=pk)).data)
        except Produto.DoesNotExist:
            return Response({'erro': 'Produto não encontrado.'}, status=404)

    def put(self, request, pk):
        try:
            dados = {k: request.data[k] for k in ['nome','descricao','preco','quantidade_estoque'] if k in request.data}
            if 'quantidade_estoque' in dados:
                dados['quantidade_estoque'] = int(dados['quantidade_estoque'])
            _svc.atualizar(pk, **dados)
            return Response({'mensagem': 'Produto atualizado com sucesso.'})
        except ValueError as e:
            return Response({'erro': str(e)}, status=400)

    def delete(self, request, pk):
        _svc.remover(pk)
        return Response({'mensagem': 'Produto removido.'})

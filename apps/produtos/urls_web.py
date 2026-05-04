from django.urls import path
from .views_web import ProdutoListView, ProdutoCreateView, ProdutoEditView, ProdutoDeleteView

urlpatterns = [
    path('',                 ProdutoListView.as_view(),   name='produto_lista'),
    path('novo/',            ProdutoCreateView.as_view(), name='produto_novo'),
    path('<int:pk>/editar/', ProdutoEditView.as_view(),   name='produto_editar'),
    path('<int:pk>/excluir/', ProdutoDeleteView.as_view(), name='produto_excluir'),
]

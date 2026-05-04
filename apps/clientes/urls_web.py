from django.urls import path
from .views_web import ClienteListView, ClienteCreateView, ClienteEditView, ClienteDeleteView

urlpatterns = [
    path('',                ClienteListView.as_view(),   name='cliente_lista'),
    path('novo/',           ClienteCreateView.as_view(), name='cliente_novo'),
    path('<int:pk>/editar/', ClienteEditView.as_view(),  name='cliente_editar'),
    path('<int:pk>/excluir/', ClienteDeleteView.as_view(), name='cliente_excluir'),
]

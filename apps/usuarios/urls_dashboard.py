from django.urls import path
from .views_web import DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]

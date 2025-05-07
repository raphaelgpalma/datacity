from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),

     # Páginas principais
    path('', views.index, name='index'),
    path('dimensoes/', views.dimensoes, name='dimensoes'),
    path('indicadores/', views.indicadores, name='indicadores'),
    path('indicadores/<str:dimensao_id>/', views.indicadores, name='indicadores_dimensao'),
    
    # APIs para dimensões
    path('api/dimensoes/', views.api_dimensoes, name='api_dimensoes'),
    path('api/dimensoes/criar/', views.criar_dimensao, name='criar_dimensao'),
    path('api/dimensoes/<str:dimensao_id>/editar/', views.editar_dimensao, name='editar_dimensao'),
    path('api/dimensoes/<str:dimensao_id>/remover/', views.remover_dimensao, name='remover_dimensao'),
    
    # APIs para indicadores
    path('api/indicadores/<str:dimensao_id>/', views.api_indicadores, name='api_indicadores'),
    path('api/indicadores/<str:dimensao_id>/adicionar/', views.adicionar_indicador, name='adicionar_indicador'),
    path('api/indicadores/<str:dimensao_id>/<str:indicador_id>/editar/', views.editar_indicador, name='editar_indicador'),
    path('api/indicadores/<str:dimensao_id>/<str:indicador_id>/excluir/', views.excluir_indicador, name='excluir_indicador'),
    
    # API para relatórios
    path('api/relatorio/<str:dimensao_id>/', views.gerar_relatorio, name='gerar_relatorio'),
    
    # Arquivos estáticos
    path('static/<path:path>', views.serve_static, name='serve_static'),
]

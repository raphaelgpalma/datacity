from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),

     # Páginas principais
    path('', views.index, name='index'),
    path('menu', views.menu, name='menu'),
    path('dimensoes/', views.dimensoes, name='dimensoes'),
    path('normas/', views.normas, name='normas'),
    path('plataformas/', views.plataformas, name='plataformas'),
    path('plataformas/csc', views.csc, name='csc'),
    path('normas/iso37120', views.iso37120, name='iso37120'),
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

    # Add these to your urlpatterns in accounts/urls.py:
    path('dashboard/', views.dashboard, name='dashboard'),
    path('indicador/<str:dimensao_id>/<int:indicador_id>/', views.indicador_detalhes, name='indicador_detalhes'),
    path('logout/', views.logout, name='logout'),

    path('modals/dimensoes/', views.modal_dimensoes, name='modal-dimensoes'),
    path('modals/indicadores/', views.modal_indicadores, name='modal-indicadores'),

    path('plataformas/adicionar/', views.adicionar_plataforma, name='adicionar_plataforma'),
    path('plataformas/editar/<int:platform_id>/', views.editar_plataforma, name='editar_plataforma'),
    path('plataformas/remover/<int:platform_id>/', views.remover_plataforma, name='remover_plataforma'),
    path('plataformas/listar/', views.listar_plataformas, name='listar_plataformas'),

    # APIs para normas
    path('normas/adicionar_norma/', views.adicionar_norma, name='adicionar_norma'),
    path('normas/editar_norma/<int:norm_id>/', views.editar_norma, name='editar_norma'),
    path('normas/remover_norma/<int:norm_id>/', views.remover_norma, name='remover_norma'),
    path('normas/listar_normas/', views.listar_normas, name='listar_normas'),
]

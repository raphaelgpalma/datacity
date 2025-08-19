from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import RegisterForm, LoginForm
from .models import User, Platform, Norm
import json
import os
from django.conf import settings
from django.utils import timezone
import mimetypes
from pathlib import Path
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from .decorators import admin_required, manager_required

# Mock data for the application
MOCK_DATA = {
    'dimensoes': [
        {'id': 'mobilidade', 'nome': 'Mobilidade', 'cor': '#FF8C00', 'ods': '9, 11', 'iso': 'ISO 37120'},
        {'id': 'urbanismo', 'nome': 'Urbanismo', 'cor': '#8A2BE2', 'ods': '11', 'iso': 'ISO 37122'},
        {'id': 'educacao', 'nome': 'Educação', 'cor': '#4CAF50', 'ods': '4', 'iso': 'ISO 37120'},
        {'id': 'seguranca', 'nome': 'Segurança', 'cor': '#00CED1', 'ods': '16', 'iso': 'ISO 37120'},
        {'id': 'governanca', 'nome': 'Governança', 'cor': '#FF00FF', 'ods': '16, 17', 'iso': 'ISO 37122'},
        {'id': 'economia', 'nome': 'Economia', 'cor': '#32CD32', 'ods': '8, 9', 'iso': 'ISO 37120'},
        {'id': 'energia', 'nome': 'Energia', 'cor': '#FF0000', 'ods': '7', 'iso': 'ISO 37120'},
        {'id': 'meio-ambiente', 'nome': 'Meio Ambiente', 'cor': '#FFD700', 'ods': '13, 14, 15', 'iso': 'ISO 37120'},
        {'id': 'tecnologia', 'nome': 'Tecnologia e Inovação', 'cor': '#1E90FF', 'ods': '9', 'iso': 'ISO 37122'},
        {'id': 'empreendedorismo', 'nome': 'Empreendedorismo', 'cor': '#FF6347', 'ods': '8', 'iso': 'ISO 37122'},
        {'id': 'saude', 'nome': 'Saúde', 'cor': '#FF6B81', 'ods': '3', 'iso': 'ISO 37120'}
    ],
    'indicadores': {
        'economia': [
            {'id': 1, 'nome': 'PIB per capita', 'ods': '8', 'dado': 'R$ 45.000,00', 'fonte': 'IBGE', 'iso': 'ISO 37120'},
            {'id': 2, 'nome': 'Taxa de desemprego', 'ods': '8', 'dado': '7,5%', 'fonte': 'IBGE', 'iso': 'ISO 37120'},
            {'id': 3, 'nome': 'Crescimento anual', 'ods': '8', 'dado': '2,3%', 'fonte': 'Secretaria de Economia', 'iso': 'ISO 37122'}
        ],
        'educacao': [
            {'id': 1, 'nome': 'Taxa de alfabetização', 'ods': '4', 'dado': '97,2%', 'fonte': 'IBGE', 'iso': 'ISO 37120'},
            {'id': 2, 'nome': 'Escolas com acesso à internet', 'ods': '4, 9', 'dado': '89%', 'fonte': 'Secretaria de Educação', 'iso': 'ISO 37122'}
        ],
        'mobilidade': [
            {'id': 1, 'nome': 'Extensão de ciclovias', 'ods': '11', 'dado': '85 km', 'fonte': 'Secretaria de Mobilidade', 'iso': 'ISO 37120'}
        ]
    }
}

# Landing page view
def landing(request):
    context = {
        'user': request.user if request.user.is_authenticated else None,
        'is_authenticated': request.user.is_authenticated
    }
    return render(request, 'landing.html', context)

# Helper function to get the next ID for a new indicator
def get_next_indicator_id(dimensao_id):
    indicadores = MOCK_DATA['indicadores'].get(dimensao_id, [])
    if not indicadores:
        return 1
    return max(ind['id'] for ind in indicadores) + 1

# Authentication views
@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                
                # Mensagem personalizada baseada no tipo de usuário
                tipo_usuario = {
                    'ADMIN': 'Administrador',
                    'MANAGER': 'Gestor',
                    'COMMON': 'Usuário Comum'
                }.get(user.user_type, 'Usuário')
                
                messages.success(request, f'Bem-vindo, {user.username}! (Nível de acesso: {tipo_usuario})')
                return redirect('menu')
            else:
                messages.error(request, 'Usuário ou senha inválidos')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('login')

# Main page views
@login_required
def index(request):
    # Pass user information to the template
    context = {
        'username': request.user.username,
        'user_type': request.user.user_type,
        'dimensoes_count': len(MOCK_DATA['dimensoes']),
        'indicadores_count': sum(len(inds) for inds in MOCK_DATA['indicadores'].values())
    }
    return render(request, 'screens/index.html', context)

@login_required
def menu(request):
    # Pass user information to the template
    context = {
        'username': request.user.username,
        'user_type': request.user.user_type,
        'dimensoes_count': len(MOCK_DATA['dimensoes']),
        'indicadores_count': sum(len(inds) for inds in MOCK_DATA['indicadores'].values())
    }
    return render(request, 'new-screens/menu.html', context)

@login_required
@require_http_methods(["GET"])
def dimensoes(request):
    context = {
        'dimensoes': MOCK_DATA['dimensoes'],
        'username': request.user.username,
        'user_type': request.user.user_type
    }
    return render(request, 'screens/dimensoes.html', context)

@login_required
@require_http_methods(["GET"])
def indicadores(request, dimensao_id=None):
    # If no dimension specified, use one from session or default to 'economia'
    if dimensao_id is None:
        dimensao_id = request.session.get('dimensao_id', 'economia')
    
    # Find dimension by ID
    dimensao = next((d for d in MOCK_DATA['dimensoes'] if d['id'] == dimensao_id), None)
    
    if not dimensao:
        messages.error(request, 'Dimensão não encontrada')
        return redirect('dimensoes')
    
    # Store selected dimension in session
    request.session['dimensao_id'] = dimensao_id
    request.session['dimensao_nome'] = dimensao['nome']
    
    # Get indicators for this dimension
    indicadores = MOCK_DATA['indicadores'].get(dimensao_id, [])
    
    context = {
        'dimensao': dimensao,
        'indicadores': indicadores,
        'dimensoes': MOCK_DATA['dimensoes'],  # For navigation menu
        'username': request.user.username,
        'user_type': request.user.user_type
    }
    
    return render(request, 'screens/indicadores.html', context)

@login_required
def normas(request):
    norms = Norm.objects.all()
    return render(request, 'accounts/normas.html', {'norms': norms})

@login_required
def plataformas(request):
    platforms = Platform.objects.all()
    return render(request, 'accounts/plataformas.html', {'platforms': platforms})

@login_required
def listar_plataformas(request):
    platforms = Platform.objects.all()
    return JsonResponse({
        'status': 'success',
        'plataformas': [
            {
                'id': p.id_plataforma,
                'name': p.Nome,
                'link': p.Direcionamento
            } for p in platforms
        ]
    })

@login_required
def adicionar_plataforma(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        link = request.POST.get('link')
        
        if not name or not link:
            return JsonResponse({
                'status': 'error',
                'message': 'Nome e link são obrigatórios'
            })
        
        try:
            platform = Platform.objects.create(
                Nome=name,
                Direcionamento=link
            )
            return JsonResponse({
                'status': 'success',
                'message': 'Plataforma adicionada com sucesso'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido'
    })

@login_required
def editar_plataforma(request, platform_id):
    if request.method == 'POST':
        platform = get_object_or_404(Platform, id_plataforma=platform_id)
        name = request.POST.get('name')
        link = request.POST.get('link')
        
        if not name or not link:
            return JsonResponse({
                'status': 'error',
                'message': 'Nome e link são obrigatórios'
            })
        
        try:
            platform.Nome = name
            platform.Direcionamento = link
            platform.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Plataforma editada com sucesso'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido'
    })

@login_required
def remover_plataforma(request, platform_id):
    if request.method == 'POST':
        platform = get_object_or_404(Platform, id_plataforma=platform_id)
        try:
            platform.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Plataforma removida com sucesso'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido'
    })

@login_required
@require_http_methods(["GET"])
def csc(request):
    context = {
        'dimensoes': MOCK_DATA['dimensoes'],
        'username': request.user.username
    }
    return render(request, 'new-screens/csc.html', context)

@login_required
@require_http_methods(["GET"])
def iso37120(request):
    context = {
        'dimensoes': MOCK_DATA['dimensoes'],
        'username': request.user.username
    }
    return render(request, 'new-screens/iso37120.html', context)

@login_required
@require_http_methods(["GET"])
def iso37122(request):
    context = {
        'dimensoes': MOCK_DATA['dimensoes'],
        'username': request.user.username
    }
    return render(request, 'new-screens/iso37122.html', context)

# API for dimensions
@require_http_methods(["GET"])
def api_dimensoes(request):
    # Check if user is logged in via API
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    return JsonResponse(MOCK_DATA['dimensoes'], safe=False)

# API for indicators
@require_http_methods(["GET"])
def api_indicadores(request, dimensao_id):
    # Check if user is logged in via API
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    # Verify if dimension exists
    if dimensao_id not in MOCK_DATA['indicadores']:
        return JsonResponse({'error': 'Dimensão não encontrada'}, status=404)
    
    indicadores = MOCK_DATA['indicadores'].get(dimensao_id, [])
    return JsonResponse(indicadores, safe=False)

# API to create a new dimension
@csrf_exempt
@require_http_methods(["POST"])
def criar_dimensao(request):
    # Check if user is logged in via API
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['id', 'nome', 'cor']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Campo obrigatório ausente: {field}'}, status=400)
        
        # Check if ID already exists
        if any(d['id'] == data['id'] for d in MOCK_DATA['dimensoes']):
            return JsonResponse({'error': 'Dimensão com este ID já existe'}, status=400)
        
        # Create new dimension
        nova_dimensao = {
            'id': data['id'],
            'nome': data['nome'],
            'cor': data['cor'],
            'ods': data.get('ods', ''),
            'iso': data.get('iso', '')
        }
        
        MOCK_DATA['dimensoes'].append(nova_dimensao)
        MOCK_DATA['indicadores'][data['id']] = []  # Initialize empty indicators list
        
        return JsonResponse(nova_dimensao, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# API to edit an existing dimension
@csrf_exempt
@require_http_methods(["PUT"])
def editar_dimensao(request, dimensao_id):
    # Check if user is logged in via API
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    try:
        data = json.loads(request.body)
        
        # Find dimension by ID
        dimensao = next((d for d in MOCK_DATA['dimensoes'] if d['id'] == dimensao_id), None)
        
        if not dimensao:
            return JsonResponse({'error': 'Dimensão não encontrada'}, status=404)
        
        # Update fields
        if 'nome' in data:
            dimensao['nome'] = data['nome']
        if 'cor' in data:
            dimensao['cor'] = data['cor']
        if 'ods' in data:
            dimensao['ods'] = data['ods']
        if 'iso' in data:
            dimensao['iso'] = data['iso']
        
        return JsonResponse(dimensao)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# API to remove a dimension
@csrf_exempt
@require_http_methods(["DELETE"])
def remover_dimensao(request, dimensao_id):
    # Check if user is logged in via API
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    # Find dimension index
    index = next((i for i, d in enumerate(MOCK_DATA['dimensoes']) if d['id'] == dimensao_id), None)
    
    if index is None:
        return JsonResponse({'error': 'Dimensão não encontrada'}, status=404)
    
    # Remove dimension
    dimensao_removida = MOCK_DATA['dimensoes'].pop(index)
    
    # Remove associated indicators
    if dimensao_id in MOCK_DATA['indicadores']:
        del MOCK_DATA['indicadores'][dimensao_id]
    
    return JsonResponse({'success': True, 'removed': dimensao_removida})

# API to add a new indicator to a dimension
@csrf_exempt
@require_http_methods(["POST"])
def adicionar_indicador(request, dimensao_id):
    # Check if user is logged in via API
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['nome', 'dado']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Campo obrigatório ausente: {field}'}, status=400)
        
        # Check if dimension exists
        if dimensao_id not in MOCK_DATA['indicadores']:
            return JsonResponse({'error': 'Dimensão não encontrada'}, status=404)
        
        # Create new indicator
        novo_indicador = {
            'id': get_next_indicator_id(dimensao_id),
            'nome': data['nome'],
            'dado': data['dado'],
            'ods': data.get('ods', ''),
            'fonte': data.get('fonte', ''),
            'iso': data.get('iso', '')
        }
        
        # Add to dimension's indicators list
        MOCK_DATA['indicadores'][dimensao_id].append(novo_indicador)
        
        return JsonResponse(novo_indicador, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# API to edit an existing indicator
@csrf_exempt
@require_http_methods(["PUT"])
def editar_indicador(request, dimensao_id, indicador_id):
    # Check if user is logged in via API
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    try:
        data = json.loads(request.body)
        indicador_id = int(indicador_id)  # Convert to integer
        
        # Check if dimension exists
        if dimensao_id not in MOCK_DATA['indicadores']:
            return JsonResponse({'error': 'Dimensão não encontrada'}, status=404)
        
        # Find the indicator
        indicador = next((ind for ind in MOCK_DATA['indicadores'][dimensao_id] if ind['id'] == indicador_id), None)
        
        if not indicador:
            return JsonResponse({'error': 'Indicador não encontrado'}, status=404)
        
        # Update fields
        if 'nome' in data:
            indicador['nome'] = data['nome']
        if 'dado' in data:
            indicador['dado'] = data['dado']
        if 'ods' in data:
            indicador['ods'] = data['ods']
        if 'fonte' in data:
            indicador['fonte'] = data['fonte']
        if 'iso' in data:
            indicador['iso'] = data['iso']
        
        return JsonResponse(indicador)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados JSON inválidos'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'ID do indicador inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# API to delete an indicator
@csrf_exempt
@require_http_methods(["DELETE"])
def excluir_indicador(request, dimensao_id, indicador_id):
    # Check if user is logged in via API
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    try:
        indicador_id = int(indicador_id)  # Convert to integer
        
        # Check if dimension exists
        if dimensao_id not in MOCK_DATA['indicadores']:
            return JsonResponse({'error': 'Dimensão não encontrada'}, status=404)
        
        # Find indicator index
        indicadores = MOCK_DATA['indicadores'][dimensao_id]
        index = next((i for i, ind in enumerate(indicadores) if ind['id'] == indicador_id), None)
        
        if index is None:
            return JsonResponse({'error': 'Indicador não encontrado'}, status=404)
        
        # Remove indicator
        indicador_removido = indicadores.pop(index)
        
        return JsonResponse({'success': True, 'removed': indicador_removido})
    
    except ValueError:
        return JsonResponse({'error': 'ID do indicador inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# API to generate a report (simulated)
@require_http_methods(["GET"])
def gerar_relatorio(request, dimensao_id):
    # Check if user is logged in via API
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    # Check if dimension exists
    if dimensao_id not in MOCK_DATA['indicadores']:
        return JsonResponse({'error': 'Dimensão não encontrada'}, status=404)
    
    # In a real scenario, you would generate a PDF or other report format
    # For now, we just return the data in a different format
    
    dimensao = next((d for d in MOCK_DATA['dimensoes'] if d['id'] == dimensao_id), None)
    indicadores = MOCK_DATA['indicadores'][dimensao_id]
    
    relatorio = {
        'titulo': f'Relatório de {dimensao["nome"]}',
        'data_geracao': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
        'dimensao': dimensao,
        'indicadores': indicadores,
        'total_indicadores': len(indicadores),
        'usuario': request.session.get('username', '')
    }
    
    return JsonResponse(relatorio)

def serve_static(request, path):
    """Improved function to serve static files."""
    # Try Django's staticfiles system first
    static_file = finders.find(path)
    if static_file:
        content_type, encoding = mimetypes.guess_type(static_file)
        if content_type is None:
            if path.endswith('.css'):
                content_type = 'text/css'
            elif path.endswith('.js'):
                content_type = 'application/javascript'
            else:
                content_type = 'application/octet-stream'
                
        return FileResponse(open(static_file, 'rb'), content_type=content_type)
    
    # If not found in staticfiles, search through various directories
    possible_paths = [
        os.path.join(settings.BASE_DIR, 'static', path),
        os.path.join(settings.BASE_DIR, 'templates', 'static', path),
    ]
    
    for file_path in possible_paths:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            content_type, encoding = mimetypes.guess_type(file_path)
            if content_type is None:
                if path.endswith('.css'):
                    content_type = 'text/css'
                elif path.endswith('.js'):
                    content_type = 'application/javascript'
                else:
                    content_type = 'application/octet-stream'
            
            return FileResponse(open(file_path, 'rb'), content_type=content_type)
    
    # If file not found
    return HttpResponse(f'Arquivo {path} não encontrado.', status=404)

# Dashboard view
def dashboard(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        return redirect('login')
    
    # Calculate some statistics for the dashboard
    total_dimensoes = len(MOCK_DATA['dimensoes'])
    total_indicadores = sum(len(inds) for inds in MOCK_DATA['indicadores'].values())
    
    # Get dimensions with most indicators
    dim_with_indicators = [(d['id'], d['nome'], len(MOCK_DATA['indicadores'].get(d['id'], []))) 
                          for d in MOCK_DATA['dimensoes']]
    dim_with_indicators.sort(key=lambda x: x[2], reverse=True)
    top_dimensions = dim_with_indicators[:5]
    
    context = {
        'username': request.session.get('username', ''),
        'total_dimensoes': total_dimensoes,
        'total_indicadores': total_indicadores,
        'top_dimensions': top_dimensions,
        'dimensoes': MOCK_DATA['dimensoes']  # For navigation
    }
    
    return render(request, 'screens/dashboard.html', context)

# View for detailed indicators
def indicador_detalhes(request, dimensao_id, indicador_id):
    # Check if user is logged in
    if 'user_id' not in request.session:
        return redirect('login')
    
    try:
        indicador_id = int(indicador_id)
        
        # Check if dimension exists
        if dimensao_id not in MOCK_DATA['indicadores']:
            messages.error(request, 'Dimensão não encontrada')
            return redirect('dimensoes')
        
        # Find the indicator
        indicador = next((ind for ind in MOCK_DATA['indicadores'][dimensao_id] if ind['id'] == indicador_id), None)
        
        if not indicador:
            messages.error(request, 'Indicador não encontrado')
            return redirect('indicadores', dimensao_id=dimensao_id)
        
        # Find the dimension
        dimensao = next((d for d in MOCK_DATA['dimensoes'] if d['id'] == dimensao_id), None)
        
        context = {
            'username': request.session.get('username', ''),
            'dimensao': dimensao,
            'indicador': indicador,
            'dimensoes': MOCK_DATA['dimensoes']  # For navigation
        }
        
        return render(request, 'screens/indicador_detalhes.html', context)
    
    except ValueError:
        messages.error(request, 'ID do indicador inválido')
        return redirect('indicadores', dimensao_id=dimensao_id)
    

    # Em accounts/views.py
def modal_dimensoes(request):
    return render(request, 'screens/modals-dimensoes.html')

def modal_indicadores(request):
    return render(request, 'screens/modals-indicadores.html')

@login_required
@manager_required
def adicionar_norma(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        link = request.POST.get('link')
        if not name or not link:
            return JsonResponse({'status': 'error', 'message': 'Nome e link são obrigatórios'})
        try:
            Norm.objects.create(Nome=name, Direcionamento=link)
            return JsonResponse({'status': 'success', 'message': 'Norma adicionada com sucesso'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'})

@login_required
@manager_required
def editar_norma(request, norm_id):
    norm = get_object_or_404(Norm, id_norma=norm_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        link = request.POST.get('link')
        
        if name and link:
            norm.Nome = name
            norm.Direcionamento = link
            norm.save()
            return JsonResponse({
                'status': 'success',
                'norm': {
                    'name': norm.Nome,
                    'link': norm.Direcionamento
                }
            })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
@manager_required
def remover_norma(request, norm_id):
    norm = get_object_or_404(Norm, id_norma=norm_id)
    
    if request.method == 'POST':
        norm.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def listar_normas(request):
    norms = list(Norm.objects.all().values('id_norma', 'Nome', 'Direcionamento'))
    # Adiciona a norma estática
    norms.append({
        'id_norma': 9999,  # Use um ID que não conflite com o banco
        'Nome': 'ISO 37120',
        'Direcionamento': 'http://localhost:8000/dashboard/normas/iso37120/'
    })
    return JsonResponse({
        'status': 'success',
        'normas': norms
    })
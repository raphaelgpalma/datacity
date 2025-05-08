from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from .models import User
import json
import os
from django.conf import settings
from django.utils import timezone
import mimetypes
from pathlib import Path
from django.contrib.staticfiles import finders
from django.templatetags.static import static

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
            user = form.save(commit=False)
            # In a real application, you would hash the password
            # For simplicity, we're keeping it as is
            user.save()
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
            try:
                user = User.objects.get(username=username, password=password)
                # In a real app, you would use Django's built-in auth system
                # For now, we'll simulate a session
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                messages.success(request, f'Bem-vindo, {user.username}!')
                return redirect('index')
            except User.DoesNotExist:
                messages.error(request, 'Usuário ou senha inválidos')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout(request):
    # Clear all session data
    request.session.flush()
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('login')

# Main page views
def index(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        return redirect('login')
    
    # Pass user information to the template
    context = {
        'username': request.session.get('username', ''),
        'dimensoes_count': len(MOCK_DATA['dimensoes']),
        'indicadores_count': sum(len(inds) for inds in MOCK_DATA['indicadores'].values())
    }
    return render(request, 'screens/index.html', context)

@require_http_methods(["GET"])
def dimensoes(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        return redirect('login')
    
    context = {
        'dimensoes': MOCK_DATA['dimensoes'],
        'username': request.session.get('username', '')
    }
    return render(request, 'screens/dimensoes.html', context)

@require_http_methods(["GET"])
def indicadores(request, dimensao_id=None):
    # Check if user is logged in
    if 'user_id' not in request.session:
        return redirect('login')
    
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
        'username': request.session.get('username', '')
    }
    
    return render(request, 'screens/indicadores.html', context)

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
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .forms import RegisterForm, LoginForm
from .models import User
import json
import os
from django.conf import settings
from django.templatetags.static import static

MOCK_DATA = {
    'dimensoes': [
        {'id': 'mobilidade', 'nome': 'Mobilidade', 'cor': '#FF8C00', 'ods': '9, 11', 'iso': 'ISO 37120'},
        {'id': 'urbanismo', 'nome': 'Urbanismo', 'cor': '#8A2BE2', 'ods': '11', 'iso': 'ISO 37122'},
        {'id': 'educacao', 'nome': 'Educação', 'cor': 'transparent', 'ods': '4', 'iso': 'ISO 37120'},
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

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(username=username, password=password)
                messages.success(request, 'Login realizado com sucesso!')
                return redirect('register')  # Pode mudar para outra página
            except User.DoesNotExist:
                messages.error(request, 'Usuário ou senha inválidos')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def get_next_indicator_id(dimensao_id):
    indicadores = MOCK_DATA['indicadores'].get(dimensao_id, [])
    if not indicadores:
        return 1
    return max(ind['id'] for ind in indicadores) + 1

def index(request):
    return render(request, 'screens/index.html')

# View da página de dimensões
def dimensoes(request):
    context = {
        'dimensoes': MOCK_DATA['dimensoes']
    }
    return render(request, 'screens/dimensoes.html', context)

# View da página de indicadores
def indicadores(request, dimensao_id=None):
    # Se a dimensão não for especificada na URL, verificar se está na sessão
    if dimensao_id is None:
        dimensao_id = request.session.get('dimensao_id', 'economia')
    
    # Encontrar a dimensão pelo ID
    dimensao = next((d for d in MOCK_DATA['dimensoes'] if d['id'] == dimensao_id), None)
    
    if not dimensao:
        # Se a dimensão não for encontrada, redirecionar para a página de dimensões
        return redirect('dimensoes')
    
    # Guardar a dimensão selecionada na sessão
    request.session['dimensao_id'] = dimensao_id
    request.session['dimensao_nome'] = dimensao['nome']
    
    # Obter os indicadores da dimensão
    indicadores = MOCK_DATA['indicadores'].get(dimensao_id, [])
    
    context = {
        'dimensao': dimensao,
        'indicadores': indicadores
    }
    
    return render(request, 'screens/indicadores.html', context)

# API para obter dados de dimensões
def api_dimensoes(request):
    return JsonResponse(MOCK_DATA['dimensoes'], safe=False)

# API para obter dados de indicadores de uma dimensão
def api_indicadores(request, dimensao_id):
    indicadores = MOCK_DATA['indicadores'].get(dimensao_id, [])
    return JsonResponse(indicadores, safe=False)

# API para criar uma nova dimensão
@csrf_exempt
def criar_dimensao(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validar dados
        required_fields = ['id', 'nome', 'cor']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Campo obrigatório ausente: {field}'}, status=400)
        
        # Verificar se o ID já existe
        if any(d['id'] == data['id'] for d in MOCK_DATA['dimensoes']):
            return JsonResponse({'error': 'Dimensão com este ID já existe'}, status=400)
        
        # Adicionar nova dimensão
        nova_dimensao = {
            'id': data['id'],
            'nome': data['nome'],
            'cor': data['cor'],
            'ods': data.get('ods', ''),
            'iso': data.get('iso', '')
        }
        
        MOCK_DATA['dimensoes'].append(nova_dimensao)
        MOCK_DATA['indicadores'][data['id']] = []  # Inicializar lista vazia de indicadores
        
        return JsonResponse(nova_dimensao, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# API para editar uma dimensão existente
@csrf_exempt
def editar_dimensao(request, dimensao_id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Encontrar a dimensão pelo ID
        dimensao = next((d for d in MOCK_DATA['dimensoes'] if d['id'] == dimensao_id), None)
        
        if not dimensao:
            return JsonResponse({'error': 'Dimensão não encontrada'}, status=404)
        
        # Atualizar campos
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

# API para remover uma dimensão
@csrf_exempt
def remover_dimensao(request, dimensao_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    # Encontrar o índice da dimensão
    index = next((i for i, d in enumerate(MOCK_DATA['dimensoes']) if d['id'] == dimensao_id), None)
    
    if index is None:
        return JsonResponse({'error': 'Dimensão não encontrada'}, status=404)
    
    # Remover a dimensão
    dimensao_removida = MOCK_DATA['dimensoes'].pop(index)
    
    # Remover também os indicadores associados
    if dimensao_id in MOCK_DATA['indicadores']:
        del MOCK_DATA['indicadores'][dimensao_id]
    
    return JsonResponse({'success': True, 'removed': dimensao_removida})

# API para adicionar um novo indicador a uma dimensão
@csrf_exempt
def adicionar_indicador(request, dimensao_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validar dados
        required_fields = ['nome', 'dado']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Campo obrigatório ausente: {field}'}, status=400)
        
        # Verificar se a dimensão existe
        if dimensao_id not in MOCK_DATA['indicadores']:
            return JsonResponse({'error': 'Dimensão não encontrada'}, status=404)
        
        # Criar novo indicador
        novo_indicador = {
            'id': get_next_indicator_id(dimensao_id),
            'nome': data['nome'],
            'dado': data['dado'],
            'ods': data.get('ods', ''),
            'fonte': data.get('fonte', ''),
            'iso': data.get('iso', '')
        }
        
        # Adicionar à lista de indicadores da dimensão
        MOCK_DATA['indicadores'][dimensao_id].append(novo_indicador)
        
        return JsonResponse(novo_indicador, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# API para editar um indicador existente
@csrf_exempt
def editar_indicador(request, dimensao_id, indicador_id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        indicador_id = int(indicador_id)  # Converter para inteiro
        
        # Verificar se a dimensão existe
        if dimensao_id not in MOCK_DATA['indicadores']:
            return JsonResponse({'error': 'Dimensão não encontrada'}, status=404)
        
        # Encontrar o indicador
        indicador = next((ind for ind in MOCK_DATA['indicadores'][dimensao_id] if ind['id'] == indicador_id), None)
        
        if not indicador:
            return JsonResponse({'error': 'Indicador não encontrado'}, status=404)
        
        # Atualizar campos
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

# API para excluir um indicador
@csrf_exempt
def excluir_indicador(request, dimensao_id, indicador_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        indicador_id = int(indicador_id)  # Converter para inteiro
        
        # Verificar se a dimensão existe
        if dimensao_id not in MOCK_DATA['indicadores']:
            return JsonResponse({'error': 'Dimensão não encontrada'}, status=404)
        
        # Encontrar o índice do indicador
        indicadores = MOCK_DATA['indicadores'][dimensao_id]
        index = next((i for i, ind in enumerate(indicadores) if ind['id'] == indicador_id), None)
        
        if index is None:
            return JsonResponse({'error': 'Indicador não encontrado'}, status=404)
        
        # Remover o indicador
        indicador_removido = indicadores.pop(index)
        
        return JsonResponse({'success': True, 'removed': indicador_removido})
    
    except ValueError:
        return JsonResponse({'error': 'ID do indicador inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# API para gerar relatório (simulado)
def gerar_relatorio(request, dimensao_id):
    # Verificar se a dimensão existe
    if dimensao_id not in MOCK_DATA['indicadores']:
        return JsonResponse({'error': 'Dimensão não encontrada'}, status=404)
    
    # Em um cenário real, aqui você geraria um PDF ou outro formato de relatório
    # Por enquanto, apenas retornamos os dados em formato diferente
    
    dimensao = next((d for d in MOCK_DATA['dimensoes'] if d['id'] == dimensao_id), None)
    indicadores = MOCK_DATA['indicadores'][dimensao_id]
    
    relatorio = {
        'titulo': f'Relatório de {dimensao["nome"]}',
        'data_geracao': 'Data atual seria inserida aqui',
        'dimensao': dimensao,
        'indicadores': indicadores,
        'total_indicadores': len(indicadores)
    }
    
    return JsonResponse(relatorio)

# Função corrigida para servir arquivos estáticos
def serve_static(request, path):
    # Tentar encontrar o arquivo em diferentes diretórios
    possible_paths = [
        os.path.join(settings.BASE_DIR, 'templates', 'screens', path),
        os.path.join(settings.BASE_DIR, 'templates', 'static', path),
        os.path.join(settings.BASE_DIR, 'static', path),
        os.path.join(settings.BASE_DIR, 'templates', path)
    ]
    
    # Verificar cada caminho possível
    for file_path in possible_paths:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Determinar o tipo de conteúdo com base na extensão do arquivo
            if path.endswith('.css'):
                content_type = 'text/css'
            elif path.endswith('.js'):
                content_type = 'application/javascript'
            elif path.endswith('.png'):
                content_type = 'image/png'
            elif path.endswith('.jpg') or path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif path.endswith('.svg'):
                content_type = 'image/svg+xml'
            elif path.endswith('.woff') or path.endswith('.woff2'):
                content_type = 'application/font-woff'
            elif path.endswith('.ttf'):
                content_type = 'application/font-ttf'
            elif path.endswith('.eot'):
                content_type = 'application/vnd.ms-fontobject'
            else:
                content_type = 'application/octet-stream'
            
            return HttpResponse(file_content, content_type=content_type)
    
    # Se não encontrar o arquivo em nenhum dos caminhos possíveis
    return HttpResponse(f'Arquivo {path} não encontrado. Caminhos verificados: {possible_paths}', status=404)
#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependências do sistema
apt-get update
apt-get install -y python3-dev libpq-dev

# Instalar dependências Python
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --no-input

# Aplicar migrações
python manage.py migrate 
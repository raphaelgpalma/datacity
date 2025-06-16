import multiprocessing

# Número de workers (processos)
workers = multiprocessing.cpu_count() * 2 + 1

# Configurações do servidor
bind = "0.0.0.0:8000"
timeout = 120
keepalive = 5

# Configurações de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190 
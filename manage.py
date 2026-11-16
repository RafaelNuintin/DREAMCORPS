#!/usr/bin/env python
"""
Atalho raiz para o manage.py do Django localizado em backend/manage.py.
Permite executar comandos como 'python manage.py runserver' a partir da raiz do projeto DREAMCORPS.
"""
import os
import sys

if __name__ == '__main__':
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    sys.path.insert(0, backend_dir)
    os.chdir(backend_dir)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dreamcorps_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. Verifique se ele está instalado."
        ) from exc
    execute_from_command_line(sys.argv)

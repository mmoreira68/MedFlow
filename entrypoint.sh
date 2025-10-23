#!/usr/bin/env bash
set -e

# Migrações e coletar estáticos sempre que sobe
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Criar superusuário se as variáveis estiverem definidas e ainda não existir
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
  echo "[entrypoint] Garantindo superusuário $DJANGO_SUPERUSER_USERNAME"
  python - <<'PYCODE'
import os
from django.contrib.auth import get_user_model
import django
django.setup()
User = get_user_model()
u = os.environ["DJANGO_SUPERUSER_USERNAME"]
e = os.environ["DJANGO_SUPERUSER_EMAIL"]
p = os.environ["DJANGO_SUPERUSER_PASSWORD"]
if not User.objects.filter(username=u).exists():
    User.objects.create_superuser(username=u, email=e, password=p)
    print(f"[entrypoint] Superusuário criado: {u}")
else:
    print(f"[entrypoint] Superusuário já existe: {u}")
PYCODE
fi

# Iniciar app
exec gunicorn project_config.wsgi --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120

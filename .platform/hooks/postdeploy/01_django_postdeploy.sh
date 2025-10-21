#!/usr/bin/env bash
set -e

echo "[postdeploy] Running Django migrate & collectstatic"

# Detecta o Python do ambiente Elastic Beanstalk
PY_BIN=$(command -v python || command -v python3)

# Executa migrações e coleta de estáticos
$PY_BIN manage.py migrate --noinput
$PY_BIN manage.py collectstatic --noinput

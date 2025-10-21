#!/usr/bin/env bash
set -e
echo "[prebuild] Upgrading pip/setuptools/wheel"
python -m pip install --upgrade pip setuptools wheel

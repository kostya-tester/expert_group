#!/usr/bin/env bash
set -e

echo "========================================"
echo " Сборка экспертной системы НК (Linux/macOS)"
echo "========================================"

pip install -r requirements.txt

pyinstaller \
  --noconfirm \
  --onedir \
  --windowed \
  --name "NK_Expert_System" \
  --add-data "assets:assets" \
  --add-data "app:app" \
  main.py

echo ""
echo "Готово! Папка: dist/NK_Expert_System/"
echo "Запуск: ./dist/NK_Expert_System/NK_Expert_System"

#!/bin/bash

# ===== CONFIGURACIÓN =====
set -e
USER="pi"
HOST="astro-pi-kit.local"
PASSWORD="1234"

REMOTE_PATH="~/Desktop/CANSAT/Satellite/Data/*"
LOCAL_PATH="BackupData"

# =========================
mkdir -p "$LOCAL_PATH"
rm -rf "$LOCAL_PATH"/*

echo "Conectando y copiando archivos..."

sshpass -p "$PASSWORD" scp -r \
    "$USER@$HOST:$REMOTE_PATH*" \
    "$LOCAL_PATH"

echo "Copia finalizada."

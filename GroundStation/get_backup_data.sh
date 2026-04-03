#!/bin/bash

# ===== CONFIGURACIÓN =====
USER="pi"
HOST="astro-pi-kit.local"
PASSWORD="1234"

REMOTE_PATH="~/Desktop/CANSAT/Satellite/Data"
LOCAL_PATH="~/Desktop/CANSAT/GroundStation/BackupData"

# =========================

echo "Conectando y copiando archivos..."

sshpass -p "$PASSWORD" scp -r \
    "$USER@$HOST:$REMOTE_PATH*" \
    "$LOCAL_PATH"

echo "Copia finalizada."

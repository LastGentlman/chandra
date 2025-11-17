#!/bin/bash
# Script para iniciar la API de Chandra con ngrok

echo "🚀 Iniciando Chandra OCR API..."

# Activar entorno virtual
cd "$(dirname "$0")"
source .venv/bin/activate

# Verificar que ngrok esté instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok no está instalado"
    echo "Instala con: sudo snap install ngrok"
    echo "O descarga desde: https://ngrok.com/download"
    exit 1
fi

# Verificar que la API no esté ya corriendo
if pgrep -f "chandra_api" > /dev/null; then
    echo "⚠️  La API ya está corriendo. Deteniendo..."
    pkill -f chandra_api
    sleep 2
fi

# Iniciar la API en segundo plano
echo "📡 Iniciando API en puerto 5000..."
chandra_api > /tmp/chandra_api.log 2>&1 &
API_PID=$!

# Esperar a que la API esté lista
echo "⏳ Esperando a que la API esté lista..."
sleep 5

# Verificar que la API esté funcionando
if ! curl -s http://localhost:5000/api/health > /dev/null; then
    echo "❌ Error: La API no está respondiendo"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo "✅ API iniciada correctamente (PID: $API_PID)"
echo ""

# Iniciar ngrok
echo "🌐 Iniciando túnel ngrok..."
echo "📋 La URL pública aparecerá abajo:"
echo ""

# Si tienes un dominio fijo configurado, úsalo:
# ngrok http 5000 --domain=tu-dominio.ngrok-free.app

# Si no, usa URL dinámica:
ngrok http 5000

# Limpiar al salir
echo ""
echo "🛑 Deteniendo servicios..."
kill $API_PID 2>/dev/null
pkill ngrok 2>/dev/null


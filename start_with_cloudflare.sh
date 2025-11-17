#!/bin/bash
# Script para iniciar la API de Chandra con Cloudflare Tunnel

echo "🚀 Iniciando Chandra OCR API con Cloudflare Tunnel..."

# Activar entorno virtual
cd "$(dirname "$0")"
source .venv/bin/activate

# Agregar cloudflared local al PATH si existe
if [ -f "$(dirname "$0")/bin/cloudflared" ]; then
    export PATH="$(dirname "$0")/bin:$PATH"
fi

# Verificar que cloudflared esté instalado
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared no está instalado"
    echo "Ejecuta: ./install_cloudflared.sh"
    exit 1
fi

# Verificar que la API no esté ya corriendo
if pgrep -f "chandra_api" > /dev/null; then
    echo "⚠️  La API ya está corriendo. Deteniendo..."
    pkill -f chandra_api
    sleep 2
fi

# Verificar si el puerto 5000 está ocupado
if command -v lsof >/dev/null 2>&1; then
    if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  El puerto 5000 ya está en uso"
        echo "Deteniendo proceso anterior..."
        pkill -f "chandra_api"
        sleep 2
    fi
elif ss -tlnp 2>/dev/null | grep -q ":5000"; then
    echo "⚠️  El puerto 5000 ya está en uso"
    echo "Deteniendo proceso anterior..."
    pkill -f "chandra_api"
    sleep 2
fi

# Iniciar la API en segundo plano
echo "📡 Iniciando API en puerto 5000..."
chandra_api > /tmp/chandra_api.log 2>&1 &
API_PID=$!

# Esperar a que la API esté lista (con reintentos)
echo "⏳ Esperando a que la API esté lista..."
MAX_RETRIES=10
RETRY_COUNT=0
API_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    sleep 2
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        API_READY=true
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Intento $RETRY_COUNT/$MAX_RETRIES..."
done

# Verificar que la API esté funcionando
if [ "$API_READY" = false ]; then
    echo "❌ Error: La API no está respondiendo después de $MAX_RETRIES intentos"
    echo ""
    echo "📋 Últimas líneas del log:"
    tail -20 /tmp/chandra_api.log
    echo ""
    kill $API_PID 2>/dev/null
    exit 1
fi

echo "✅ API iniciada correctamente (PID: $API_PID)"
echo ""

# Verificar si hay un túnel configurado
if [ ! -f ~/.cloudflared/config.yml ]; then
    echo "⚠️  No se encontró configuración de Cloudflare Tunnel"
    echo ""
    echo "Primero necesitas configurar el túnel:"
    echo "1. cloudflared tunnel login"
    echo "2. cloudflared tunnel create chandra-api"
    echo "3. Configurar ~/.cloudflared/config.yml"
    echo ""
    echo "Ver EXPOSE_API.md para más detalles"
    exit 1
fi

# Iniciar Cloudflare Tunnel
echo "🌐 Iniciando Cloudflare Tunnel..."
echo "📋 La URL pública aparecerá abajo:"
echo ""

cloudflared tunnel run chandra-api

# Limpiar al salir
echo ""
echo "🛑 Deteniendo servicios..."
kill $API_PID 2>/dev/null


#!/bin/bash
# Script para iniciar vLLM con GPU y exponerlo con Cloudflare Tunnel

echo "🚀 Iniciando vLLM con GPU y Cloudflare Tunnel..."

# Activar entorno virtual
cd "$(dirname "$0")"
source .venv/bin/activate

# Agregar cloudflared local al PATH si existe
if [ -f "$(dirname "$0")/bin/cloudflared" ]; then
    export PATH="$(dirname "$0")/bin:$PATH"
fi

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Inicia Docker primero."
    exit 1
fi

# Verificar que nvidia-docker esté disponible
if ! docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi > /dev/null 2>&1; then
    echo "⚠️  Advertencia: No se pudo verificar acceso a GPU. Continuando de todas formas..."
fi

# Verificar que el puerto 5000 no esté ocupado
if command -v lsof >/dev/null 2>&1; then
    if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  El puerto 5000 ya está en uso"
        echo "Deteniendo contenedores vLLM anteriores..."
        docker ps | grep vllm | awk '{print $1}' | xargs -r docker stop
        sleep 2
    fi
elif ss -tlnp 2>/dev/null | grep -q ":5000"; then
    echo "⚠️  El puerto 5000 ya está en uso"
    echo "Deteniendo contenedores vLLM anteriores..."
    docker ps | grep vllm | awk '{print $1}' | xargs -r docker stop
    sleep 2
fi

# Iniciar vLLM en segundo plano
echo "📡 Iniciando vLLM en puerto 5000 (mapeado desde 8000 interno)..."
chandra_vllm > /tmp/chandra_vllm.log 2>&1 &
VLLM_PID=$!

# Esperar a que vLLM esté listo
echo "⏳ Esperando a que vLLM esté listo (esto puede tardar varios minutos la primera vez)..."
MAX_RETRIES=30
RETRY_COUNT=0
VLLM_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    sleep 5
    if curl -s http://localhost:5000/v1/models > /dev/null 2>&1; then
        VLLM_READY=true
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Intento $RETRY_COUNT/$MAX_RETRIES..."
done

# Verificar que vLLM esté funcionando
if [ "$VLLM_READY" = false ]; then
    echo "❌ Error: vLLM no está respondiendo después de $MAX_RETRIES intentos"
    echo ""
    echo "📋 Últimas líneas del log:"
    tail -20 /tmp/chandra_vllm.log
    echo ""
    kill $VLLM_PID 2>/dev/null
    docker ps | grep vllm | awk '{print $1}' | xargs -r docker stop
    exit 1
fi

echo "✅ vLLM iniciado correctamente en puerto 5000"
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
    echo "Ver SETUP_CLOUDFLARE.md para más detalles"
    exit 1
fi

# Iniciar Cloudflare Tunnel
echo "🌐 Iniciando Cloudflare Tunnel..."
if [ -n "$PUBLIC_VLLM_URL" ]; then
    echo "📋 vLLM estará disponible en: $PUBLIC_VLLM_URL"
else
    echo "📋 Define PUBLIC_VLLM_URL para mostrar la URL pública que expone tu túnel (ej: https://tunnel.midominio.com/v1)"
fi
echo "   (El túnel ya está configurado para exponer el puerto 5000)"
echo ""

cloudflared tunnel run chandra-api

# Limpiar al salir
echo ""
echo "🛑 Deteniendo servicios..."
kill $VLLM_PID 2>/dev/null
docker ps | grep vllm | awk '{print $1}' | xargs -r docker stop


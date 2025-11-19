#!/bin/bash
# Script para iniciar vLLM con GPU y exponerlo públicamente con túnel

echo "🚀 Iniciando vLLM con GPU..."

# Activar entorno virtual
cd "$(dirname "$0")"
source .venv/bin/activate

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Inicia Docker primero."
    exit 1
fi

# Verificar que nvidia-docker esté disponible
if ! docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi > /dev/null 2>&1; then
    echo "⚠️  Advertencia: No se pudo verificar acceso a GPU. Continuando de todas formas..."
fi

# Verificar que el puerto 8000 no esté ocupado
if command -v lsof >/dev/null 2>&1; then
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  El puerto 8000 ya está en uso"
        echo "Deteniendo proceso anterior..."
        docker ps | grep vllm | awk '{print $1}' | xargs -r docker stop
        sleep 2
    fi
fi

# Iniciar vLLM en segundo plano
echo "📡 Iniciando vLLM en puerto 8000..."
chandra_vllm > /tmp/chandra_vllm.log 2>&1 &
VLLM_PID=$!

# Esperar a que vLLM esté listo
echo "⏳ Esperando a que vLLM esté listo (esto puede tardar varios minutos la primera vez)..."
MAX_RETRIES=30
RETRY_COUNT=0
VLLM_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    sleep 5
    if curl -s http://localhost:8000/v1/models > /dev/null 2>&1; then
        VLLM_READY=true
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Intento $RETRY_COUNT/$MAX_RETRIES..."
done

# Verificar que vLLM esté funcionando
if [ "$VLLM_READY" = false ]; then
    echo "❌ Error: vLLM no está respondiendo después de $MAX_RETRIES intentos"
    echo "Revisa los logs: tail -f /tmp/chandra_vllm.log"
    kill $VLLM_PID 2>/dev/null
    exit 1
fi

echo "✅ vLLM iniciado correctamente"
echo ""

# Verificar si ngrok está disponible
if command -v ngrok &> /dev/null; then
    echo "🌐 Iniciando túnel ngrok para exponer vLLM..."
    echo "📋 La URL pública aparecerá abajo:"
    echo "⚠️  IMPORTANTE: Copia la URL HTTPS (ej: https://abc123.ngrok-free.app)"
    echo "   y configúrala en Railway como: VLLM_API_BASE=https://abc123.ngrok-free.app/v1"
    echo ""
    
    # Iniciar ngrok
    ngrok http 8000
    
    # Limpiar al salir
    echo ""
    echo "🛑 Deteniendo servicios..."
    kill $VLLM_PID 2>/dev/null
    docker ps | grep vllm | awk '{print $1}' | xargs -r docker stop
    pkill ngrok 2>/dev/null
elif [ -f "$(dirname "$0")/bin/cloudflared" ]; then
    echo "🌐 Iniciando túnel Cloudflare para exponer vLLM..."
    export PATH="$(dirname "$0")/bin:$PATH"
    
    # Verificar si hay un túnel configurado para vLLM
    if cloudflared tunnel list | grep -q "chandra-vllm"; then
        echo "✅ Túnel 'chandra-vllm' encontrado"
        cloudflared tunnel run chandra-vllm
    else
        echo "⚠️  No se encontró túnel 'chandra-vllm'"
        echo "Crea uno con: cloudflared tunnel create chandra-vllm"
        echo "Y configura el DNS para apuntar al puerto 8000"
        echo ""
        echo "Por ahora, puedes usar ngrok: ngrok http 8000"
    fi
else
    echo "⚠️  No se encontró ngrok ni cloudflared"
    echo "Instala uno de ellos para exponer vLLM públicamente:"
    echo "  - ngrok: sudo snap install ngrok"
    echo "  - cloudflared: ./install_cloudflared.sh"
    echo ""
    echo "vLLM está corriendo en http://localhost:8000"
    echo "Presiona Ctrl+C para detenerlo"
    
    # Esperar hasta que se presione Ctrl+C
    wait $VLLM_PID
fi


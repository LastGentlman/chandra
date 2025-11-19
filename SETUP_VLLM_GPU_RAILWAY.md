# Configurar vLLM con GPU local + API en Railway

Esta guía explica cómo usar tu GPU local para vLLM mientras la API corre en Railway.

## Arquitectura

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────┐
│   Tu PC (GPU)   │         │ Cloudflare Tunnel│         │   Railway    │
│                 │         │                  │         │              │
│  vLLM :5000     │ ──────> │ chandra-vllm.    │ ──────> │  API :5000   │
│  (GPU)          │         │ ingroy.com       │         │              │
└─────────────────┘         └──────────────────┘         └──────────────┘
```

**Nota:** vLLM usa el puerto 5000 (mapeado desde el puerto 8000 interno de Docker).

## Paso 1: Iniciar vLLM con GPU y Cloudflare Tunnel

Ya tienes Cloudflare Tunnel configurado. Solo necesitas iniciar vLLM:

```bash
cd ~/Desktop/chandra
./start_vllm_cloudflare.sh
```

Este script:
1. ✅ Inicia vLLM con GPU en el puerto 5000
2. ✅ Espera a que esté listo
3. ✅ Inicia Cloudflare Tunnel (ya configurado)
4. ✅ Expone vLLM en: `https://chandra-vllm.ingroy.com/v1`

### Verificar que vLLM funciona

```bash
# En otra terminal
curl http://localhost:5000/v1/models
```

Deberías ver una respuesta JSON con el modelo "chandra".

## Paso 2: Configurar Railway

### Variables de entorno en Railway

#### Servicio API en Railway:

```
# URL del vLLM público (usando tu Cloudflare Tunnel)
VLLM_API_BASE=https://chandra-vllm.ingroy.com/v1

# Nombre del modelo
VLLM_MODEL_NAME=chandra

# API key (vLLM no requiere autenticación por defecto)
VLLM_API_KEY=EMPTY

# Autenticación de la API
CHANDRA_API_KEY=chandra_live_a8f7b9052593f7bb773f8d3cb4f893b3be56b5fd81f1013b6281feb36ed25d62
CHANDRA_REQUIRE_API_KEY=true
```

#### Servicio Bot en Railway (si tienes uno):

```
# Token de Telegram
TELEGRAM_BOT_TOKEN=8503190770:AAG438RJS1diQ2SZlVythH15Lrwa1yR6mfA

# URL de la API (URL pública de tu API en Railway)
CHANDRA_API_URL=https://tu-api-en-railway.railway.app/api/ocr/image

# API Key (debe ser la MISMA que en la API)
CHANDRA_API_KEY=chandra_live_a8f7b9052593f7bb773f8d3cb4f893b3be56b5fd81f1013b6281feb36ed25d62
```

**⚠️ IMPORTANTE:** 
- `CHANDRA_API_KEY` debe ser **exactamente la misma** en API y Bot
- `CHANDRA_API_URL` debe ser la URL completa del endpoint de tu API en Railway

### Verificar que Railway se conecta

Después de desplegar, verifica los logs de Railway. Deberías ver que la API se conecta correctamente a vLLM.

**Ver también:** `ENV_VARIABLES.md` para un resumen completo de todas las variables de entorno.

## Solución de problemas

### vLLM no inicia

```bash
# Ver logs
tail -f /tmp/chandra_vllm.log

# Verificar GPU
nvidia-smi

# Verificar Docker
docker ps
```

### Railway no se conecta a vLLM

1. Verifica que el túnel esté activo
2. Verifica que la URL en Railway sea correcta (debe terminar en `/v1`)
3. Prueba la URL desde tu navegador: `https://tu-url/v1/models`

### La URL de ngrok cambia

La versión gratuita de ngrok cambia la URL cada vez. Opciones:
- Usa Cloudflare Tunnel (URL permanente)
- Actualiza `VLLM_API_BASE` en Railway cada vez
- Usa un dominio fijo de ngrok (requiere plan de pago)

## Resumen de comandos

```bash
# En tu PC: Iniciar vLLM con Cloudflare Tunnel
cd ~/Desktop/chandra
./start_vllm_cloudflare.sh

# En Railway: Configurar
VLLM_API_BASE=https://chandra-vllm.ingroy.com/v1
```

## Notas importantes

- ⚠️ **Mantén vLLM y el túnel corriendo** mientras Railway necesite usarlo
- ⚠️ **La URL de ngrok cambia** cada vez que reinicias (versión gratuita)
- ✅ **Cloudflare Tunnel** es mejor para producción (URL permanente)
- 💰 **Costo**: vLLM usa tu GPU local (gratis), Railway solo corre la API (más barato)


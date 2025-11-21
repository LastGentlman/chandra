# Variables de Entorno - Resumen Completo

> ⚠️ **Nunca** publiques valores reales de tokens o API keys en repositorios, tickets o capturas. Usa `local.env` (ignorad@ por git) y administradores de secretos como Railway, Fly.io, Render o GitHub Actions Secrets.

## 📋 Resumen por componente

### 1. vLLM en tu PC (`local.env`)

```bash
# Configuración del servidor vLLM local
VLLM_API_BASE=http://localhost:5000/v1
VLLM_MODEL_NAME=chandra
VLLM_GPUS=0                  # Ej: "0,1" para dos GPUs
VLLM_API_KEY=EMPTY           # Sólo si tu túnel exige autenticación

# Autenticación / seguridad compartida con la API
CHANDRA_API_KEY=<TU_CHANDRA_API_KEY>
CHANDRA_REQUIRE_API_KEY=true
CHANDRA_ALLOWED_ORIGINS=http://localhost:3000
CHANDRA_MAX_UPLOAD_MB=25
CHANDRA_MAX_IMAGE_PIXELS=80000000
```

Guarda el archivo como `local.env` (basado en `local.env.example`) para evitar exponer credenciales.

---

### 2. API en Railway (o cualquier PaaS)

```bash
# Enlace hacia tu vLLM público (Cloudflare Tunnel, ngrok, etc.)
VLLM_API_BASE=https://<tu-tunel-publico>.example.com/v1
VLLM_MODEL_NAME=chandra
VLLM_API_KEY=EMPTY                       # o el token del túnel si aplica

# Seguridad de la API HTTP
CHANDRA_API_KEY=<TU_CHANDRA_API_KEY>
CHANDRA_REQUIRE_API_KEY=true
CHANDRA_ALLOWED_ORIGINS=https://app.midominio.com
CHANDRA_MAX_UPLOAD_MB=25
CHANDRA_MAX_IMAGE_PIXELS=80000000

# Railway define PORT automáticamente; no lo hardcodees.
```

---

### 3. Bot (Railway, Fly, etc.)

```bash
TELEGRAM_BOT_TOKEN=<TOKEN_DE_TELEGRAM>
CHANDRA_API_URL=https://tu-api-en-railway.app/api/ocr/image
CHANDRA_API_KEY=<TU_CHANDRA_API_KEY>     # Debe ser idéntica a la de la API
```

Nunca compartas el `TELEGRAM_BOT_TOKEN`; revoca y crea uno nuevo si llegó a filtrarse.

---

## 🔑 Variables críticas

- **`CHANDRA_API_KEY`**: clave simétrica para proteger tus endpoints. Usa valores largos, generados aleatoriamente y distintos por entorno. Debe coincidir en:
  - API pública (Railway / servidor propio)
  - Bot / integraciones
  - Pruebas locales (`local.env`)
- **`VLLM_API_BASE`**: endpoint del backend vLLM que realmente ejecuta la inferencia. Nunca dejes una URL pública sin autenticación adicional (túnel protegido, firewall, VPN, etc.).

---

## ✅ Checklist rápido

**Servicio API (Railway)**
- [ ] `VLLM_API_BASE=https://<tu-tunel-publico>.example.com/v1`
- [ ] `CHANDRA_API_KEY=<token-generado>`
- [ ] `CHANDRA_REQUIRE_API_KEY=true`
- [ ] `CHANDRA_ALLOWED_ORIGINS=https://app.midominio.com`
- [ ] `CHANDRA_MAX_UPLOAD_MB=25` (ajusta según tus límites)

**Servicio del Bot**
- [ ] `TELEGRAM_BOT_TOKEN=<token de BotFather>`
- [ ] `CHANDRA_API_URL=https://<tu-api>/api/ocr/image`
- [ ] `CHANDRA_API_KEY=<mismo token que la API>`

**Entorno local (`local.env`)**
- [ ] `VLLM_API_BASE=http://localhost:5000/v1`
- [ ] `VLLM_GPUS=<ids disponibles>`
- [ ] `CHANDRA_API_KEY=<token local>`
- [ ] `CHANDRA_ALLOWED_ORIGINS=http://localhost:3000`

---

## 🚨 Variables y flags opcionales

```bash
# API HTTP
HOST=0.0.0.0          # default
DEBUG=false           # nunca actives en producción
PORT=5000             # gestionado por Railway/Fly

# vLLM
MAX_VLLM_RETRIES=6
MODEL_CHECKPOINT=datalab-to/chandra
MAX_OUTPUT_TOKENS=12384
```

- `CHANDRA_ALLOWED_ORIGINS`: lista separada por comas de orígenes confiables (`https://app.midominio.com,https://panel.midominio.com`). Usa `*` sólo para desarrollo.
- `CHANDRA_MAX_UPLOAD_MB`: controla el límite superior aceptado por los endpoints `/api/ocr` y `/api/ocr/image`.
- `CHANDRA_MAX_IMAGE_PIXELS`: freno contra imágenes maliciosas/ZIP bombs.

---

## 📝 Buenas prácticas

1. **Gestiona secretos fuera del repositorio**: usa `local.env` (ignorado por git) y los paneles de secretos de Railway/Fly/docker compose.
2. **Rotación**: ante cualquier sospecha, genera un nuevo `CHANDRA_API_KEY` o `TELEGRAM_BOT_TOKEN` y actualiza todos los servicios dependientes.
3. **Principio de mínimo privilegio**: no reutilices el mismo token para distintos proyectos o bots.
4. **Revisa el historial**: si un secreto se publicó por error, bórralo del historial (BFG/git filter-repo) y considera comprometerlo como expuesto permanentemente.



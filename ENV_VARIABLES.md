# Variables de Entorno - Resumen Completo

## 📋 Resumen por Componente

### 1. vLLM en tu PC (local) - `local.env`

```bash
# Configuración de vLLM (para usar GPU local)
VLLM_API_BASE=http://localhost:5000/v1
VLLM_MODEL_NAME=chandra
VLLM_GPUS=0  # Cambia si tienes múltiples GPUs (ej: "0,1" para GPU 0 y 1)
VLLM_API_KEY=EMPTY
```

**Nota:** Estas variables están en `local.env` y se usan cuando ejecutas `chandra_vllm` localmente.

---

### 2. API en Railway

```bash
# Conexión a vLLM (tu PC con GPU)
VLLM_API_BASE=https://chandra-vllm.ingroy.com/v1
VLLM_MODEL_NAME=chandra
VLLM_API_KEY=EMPTY

# Autenticación de la API
CHANDRA_API_KEY=chandra_live_a8f7b9052593f7bb773f8d3cb4f893b3be56b5fd81f1013b6281feb36ed25d62
CHANDRA_REQUIRE_API_KEY=true

# Puerto (Railway lo configura automáticamente)
PORT=5000  # No necesitas configurarlo, Railway lo hace
```

**Importante:** 
- `VLLM_API_BASE` debe apuntar a tu vLLM expuesto públicamente
- `CHANDRA_API_KEY` debe ser la misma que uses en el bot

---

### 3. Bot en Railway

```bash
# Token de Telegram
TELEGRAM_BOT_TOKEN=8503190770:AAG438RJS1diQ2SZlVythH15Lrwa1yR6mfA

# URL de la API (debe ser la URL pública de tu API en Railway)
CHANDRA_API_URL=https://tu-api-en-railway.railway.app/api/ocr/image
# O si tienes un dominio personalizado:
# CHANDRA_API_URL=https://api.tu-dominio.com/api/ocr/image

# API Key para autenticarse con la API (debe ser la MISMA que en la API)
CHANDRA_API_KEY=chandra_live_a8f7b9052593f7bb773f8d3cb4f893b3be56b5fd81f1013b6281feb36ed25d62
```

**Importante:**
- `CHANDRA_API_KEY` debe ser **exactamente la misma** que configuraste en la API
- `CHANDRA_API_URL` debe ser la URL completa del endpoint de la API en Railway

---

## 🔑 Variables Críticas

### CHANDRA_API_KEY
- **Debe ser la misma** en:
  - ✅ API en Railway
  - ✅ Bot en Railway
  - ✅ `local.env` (si pruebas localmente)

### VLLM_API_BASE
- **En tu PC (local.env):** `http://localhost:5000/v1`
- **En Railway (API):** `https://chandra-vllm.ingroy.com/v1`

---

## ✅ Checklist de Configuración

### En Railway - Servicio API:
- [ ] `VLLM_API_BASE=https://chandra-vllm.ingroy.com/v1`
- [ ] `VLLM_MODEL_NAME=chandra`
- [ ] `VLLM_API_KEY=EMPTY`
- [ ] `CHANDRA_API_KEY=chandra_live_a8f7b9052593f7bb773f8d3cb4f893b3be56b5fd81f1013b6281feb36ed25d62`
- [ ] `CHANDRA_REQUIRE_API_KEY=true`

### En Railway - Servicio Bot:
- [ ] `TELEGRAM_BOT_TOKEN=8503190770:AAG438RJS1diQ2SZlVythH15Lrwa1yR6mfA`
- [ ] `CHANDRA_API_URL=https://tu-api-en-railway.railway.app/api/ocr/image`
- [ ] `CHANDRA_API_KEY=chandra_live_a8f7b9052593f7bb773f8d3cb4f893b3be56b5fd81f1013b6281feb36ed25d62`

### En tu PC - local.env:
- [ ] `VLLM_API_BASE=http://localhost:5000/v1`
- [ ] `VLLM_MODEL_NAME=chandra`
- [ ] `VLLM_GPUS=0`
- [ ] `VLLM_API_KEY=EMPTY`
- [ ] `CHANDRA_API_KEY=chandra_live_a8f7b9052593f7bb773f8d3cb4f893b3be56b5fd81f1013b6281feb36ed25d62`
- [ ] `CHANDRA_REQUIRE_API_KEY=true`

---

## 🚨 Variables Opcionales

Estas tienen valores por defecto, pero puedes configurarlas si necesitas:

```bash
# Para la API
HOST=0.0.0.0  # Por defecto
DEBUG=false   # Por defecto
PORT=5000     # Por defecto (Railway lo configura automáticamente)

# Para vLLM
MAX_VLLM_RETRIES=6  # Por defecto
MODEL_CHECKPOINT=datalab-to/chandra  # Por defecto
MAX_OUTPUT_TOKENS=12384  # Por defecto
```

---

## 📝 Notas Importantes

1. **CHANDRA_API_KEY debe ser idéntica** en API y Bot
2. **VLLM_API_BASE** en Railway debe apuntar a tu vLLM público
3. **CHANDRA_API_URL** en el bot debe ser la URL completa del endpoint
4. **PORT** en Railway se configura automáticamente, no necesitas configurarlo
5. Si cambias `CHANDRA_API_KEY`, actualízala en todos los lugares


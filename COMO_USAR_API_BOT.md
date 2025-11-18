# Cómo obtener y usar la API para tu bot

## 🤖 Paso 0: Obtener el Token de Telegram (si estás haciendo un bot de Telegram)

Para crear un bot de Telegram, necesitas obtener un **token** de @BotFather:

### 1. Abre Telegram y busca @BotFather
- Busca `@BotFather` en Telegram
- O ve directamente a: https://t.me/BotFather

### 2. Crea un nuevo bot
Envía el comando:
```
/newbot
```

### 3. Sigue las instrucciones
- Elige un **nombre** para tu bot (ej: "Mi Bot OCR")
- Elige un **username** único que termine en `bot` (ej: `mi_bot_ocr_bot`)

### 4. Obtén tu token
BotFather te dará un token que se ve así:
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

⚠️ **IMPORTANTE:** Guarda este token de forma segura. Es como la contraseña de tu bot.

### 5. Configurar el token en tu código

**Opción A: Variable de entorno (recomendado)**
```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

**Opción B: Archivo .env**
Crea un archivo `.env`:
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
CHANDRA_API_URL=http://localhost:5000
```

Luego en tu código Python:
```python
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
```

**Opción C: Directamente en el código (no recomendado para producción)**
```python
TELEGRAM_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

---

## 🚀 Paso 1: Iniciar el servidor de la API

La API **no requiere una API key**. Solo necesitas iniciar el servidor:

```bash
chandra_api
```

Esto iniciará el servidor en `http://localhost:5000` por defecto.

### Para ejecutarlo en segundo plano:

```bash
chandra_api > /tmp/chandra_api.log 2>&1 &
```

### Para cambiar el puerto (opcional):

```bash
PORT=8080 chandra_api
```

## 📍 Paso 2: Obtener la URL de la API

Dependiendo de dónde esté tu bot, usa una de estas URLs:

### Si el bot está en la misma máquina:
```
http://localhost:5000
```

### Si el bot está en otra máquina de tu red local:
Primero obtén tu IP local:
```bash
hostname -I
```

Luego usa:
```
http://TU_IP_LOCAL:5000
```
Ejemplo: `http://192.168.1.57:5000`

### Si el bot está en internet (fly.io, Railway, etc.):
Necesitas exponer la API a internet. Ver `EXPOSE_API.md` para opciones:
- **Cloudflare Tunnel** (recomendado, gratis)
- **ngrok** (rápido, gratis pero URL cambia)
- **localtunnel** (gratis, sin registro)

## ✅ Paso 3: Verificar que la API funciona

```bash
curl http://localhost:5000/api/health
```

Deberías recibir:
```json
{"status":"ok","service":"chandra-ocr-api"}
```

## 🔧 Paso 4: Usar la API en tu bot

### Ejemplo completo: Bot de Telegram

```python
import requests
import os
import base64
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Configuración
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Tu token de @BotFather
CHANDRA_API_URL = "http://localhost:5000/api/ocr/image"  # Ajusta según tu caso

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa fotos enviadas al bot"""
    await update.message.reply_text("Procesando imagen...")
    
    photo = update.message.photo[-1]  # Obtener la foto de mayor resolución
    
    # Descargar la foto
    file = await context.bot.get_file(photo.file_id)
    file_path = await file.download()
    
    # Convertir a base64
    with open(file_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()
        image_data = f"data:image/jpeg;base64,{image_base64}"
    
    # Procesar con Chandra
    try:
        response = requests.post(
            CHANDRA_API_URL,
            json={"image_base64": image_data, "method": "vllm"},
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        # Enviar resultado al usuario
        text = result["markdown"][:4000]  # Limitar a 4000 caracteres (límite de Telegram)
        await update.message.reply_text(f"Texto extraído:\n\n{text}")
        
    except Exception as e:
        await update.message.reply_text(f"Error procesando imagen: {e}")
    
    # Limpiar archivo temporal
    os.remove(file_path)

# Configurar bot
def main():
    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN no está configurado")
        print("Obtén tu token de @BotFather en Telegram")
        return
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot iniciado. Esperando fotos...")
    app.run_polling()

if __name__ == "__main__":
    main()
```

### Ejemplo básico en Python (sin Telegram):

```python
import requests
import base64

# URL de la API (ajusta según tu caso)
API_URL = "http://localhost:5000"  # O tu IP pública si está en otra máquina

# Procesar imagen desde base64
def procesar_imagen(image_base64):
    url = f"{API_URL}/api/ocr/image"
    payload = {
        "image_base64": image_base64,
        "method": "vllm"
    }
    response = requests.post(url, json=payload)
    return response.json()

# Ejemplo de uso
resultado = procesar_imagen("data:image/png;base64,iVBORw0KGgo...")
print(resultado["markdown"])
```

### Endpoints disponibles:

1. **Health check:**
   ```
   GET /api/health
   ```

2. **Procesar archivo:**
   ```
   POST /api/ocr
   Content-Type: multipart/form-data
   - file: archivo (imagen o PDF)
   - method: "vllm" o "hf"
   ```

3. **Procesar imagen base64 (recomendado para bots):**
   ```
   POST /api/ocr/image
   Content-Type: application/json
   {
     "image_base64": "data:image/png;base64,...",
     "method": "vllm"
   }
   ```

## 📦 Instalación de dependencias para bot de Telegram

Si vas a hacer un bot de Telegram, instala la librería:

```bash
pip install python-telegram-bot requests python-dotenv
```

O si usas `uv`:
```bash
uv pip install python-telegram-bot requests python-dotenv
```

## 📚 Más información

- **Ejemplo completo de bot:** Ver `example_bot_integration.py`
- **Documentación completa:** Ver `BOT_ACCESS.md`
- **Exponer a internet:** Ver `EXPOSE_API.md`
- **Documentación de la API:** Ver `API_DOCS.md`
- **Documentación de python-telegram-bot:** https://python-telegram-bot.org/

## 🔒 Nota sobre seguridad

La API actualmente **no tiene autenticación**. Si la vas a exponer públicamente, considera:
- Agregar API keys
- Usar HTTPS
- Configurar rate limiting
- Ver sección "Seguridad" en `BOT_ACCESS.md`


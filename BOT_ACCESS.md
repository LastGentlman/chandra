# Cómo acceder a la API desde tu bot

La API de Chandra OCR ya está configurada con CORS y lista para ser usada desde tu bot.

## URLs de acceso

### Desde la misma máquina (localhost):
```
http://localhost:5000
```

### Desde otra máquina en la misma red:
```
http://192.168.1.57:5000
```

### Si tienes un dominio o IP pública:
```
http://TU_IP_PUBLICA:5000
```

## Ejemplos de uso desde el bot

### 1. Python (requests)

```python
import requests
import base64

# URL de la API (ajusta según tu caso)
API_URL = "http://192.168.1.57:5000"  # O "http://localhost:5000" si está en la misma máquina

# Opción A: Procesar imagen desde archivo
def process_image_file(image_path):
    url = f"{API_URL}/api/ocr"
    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
        return response.json()

# Opción B: Procesar imagen desde base64 (útil para bots)
def process_image_base64(image_base64):
    url = f"{API_URL}/api/ocr/image"
    payload = {
        "image_base64": image_base64
    }
    response = requests.post(url, json=payload)
    return response.json()

# Ejemplo de uso
result = process_image_base64("data:image/png;base64,iVBORw0KGgo...")
print(result["markdown"])
```

### 2. JavaScript/Node.js (fetch)

```javascript
// URL de la API
const API_URL = "http://192.168.1.57:5000";

// Procesar imagen desde base64
async function processImage(imageBase64) {
    const response = await fetch(`${API_URL}/api/ocr/image`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
            body: JSON.stringify({
                image_base64: imageBase64
            })
    });
    
    return await response.json();
}

// Ejemplo de uso
const result = await processImage("data:image/png;base64,...");
console.log(result.markdown);
```

### 3. cURL (para pruebas)

```bash
# Health check
curl http://192.168.1.57:5000/api/health

# Procesar archivo
curl -X POST http://192.168.1.57:5000/api/ocr \
  -F "file=@imagen.png"

# Procesar imagen base64
curl -X POST http://192.168.1.57:5000/api/ocr/image \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "data:image/png;base64,..."}'
```

## Ejemplo completo: Bot de Telegram

```python
import requests
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Configuración
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANDRA_API_URL = "http://192.168.1.57:5000/api/ocr/image"  # Ajusta la URL

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa fotos enviadas al bot"""
    photo = update.message.photo[-1]  # Obtener la foto de mayor resolución
    
    # Descargar la foto
    file = await context.bot.get_file(photo.file_id)
    file_path = await file.download()
    
    # Convertir a base64
    import base64
    with open(file_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()
        image_data = f"data:image/jpeg;base64,{image_base64}"
    
    # Procesar con Chandra
    try:
        response = requests.post(
            CHANDRA_API_URL,
            json={"image_base64": image_data},
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
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
```

## Verificar que la API está accesible

### Desde la misma máquina:
```bash
curl http://localhost:5000/api/health
```

### Desde otra máquina en la red:
```bash
curl http://192.168.1.57:5000/api/health
```

Si recibes `{"status":"ok","service":"chandra-ocr-api"}`, la API está funcionando correctamente.

## Solución de problemas

### 1. No puedo acceder desde otra máquina

**Problema:** El firewall está bloqueando el puerto 5000.

**Solución:**
```bash
# Ubuntu/Debian
sudo ufw allow 5000/tcp

# O abrir el puerto específicamente
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

### 2. Error de conexión

**Verifica:**
- Que el servidor esté corriendo: `ps aux | grep chandra_api`
- Que el puerto esté abierto: `ss -tlnp | grep 5000`
- Que la IP sea correcta: `hostname -I`

### 3. CORS errors (en navegadores)

La API ya tiene CORS configurado. Si aún tienes problemas, verifica que el servidor se haya reiniciado después de los cambios.

## Seguridad (para producción)

Si vas a exponer la API públicamente, considera:

1. **Agregar autenticación:**
   - API keys
   - Tokens JWT
   - Basic Auth

2. **Usar HTTPS:**
   - Configurar un proxy reverso (nginx) con SSL
   - O usar un servicio como Cloudflare

3. **Limitar acceso:**
   - Firewall rules
   - Rate limiting
   - IP whitelist

4. **Cambiar el puerto:**
   ```bash
   PORT=8080 chandra_api
   ```

## Estado actual del servidor

- ✅ CORS habilitado (accesible desde cualquier origen)
- ✅ Escuchando en `0.0.0.0:5000` (accesible desde la red)
- ✅ Endpoints disponibles:
  - `GET /api/health` - Health check
  - `POST /api/ocr` - Procesar archivo
  - `POST /api/ocr/image` - Procesar imagen base64


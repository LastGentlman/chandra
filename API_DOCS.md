# API REST de Chandra OCR

API REST para procesar imágenes y PDFs con Chandra OCR, ideal para integrar en bots y aplicaciones.

## Iniciar el servidor

```bash
# Opción 1: Usando el comando instalado
chandra_api

# Opción 2: Directamente con Python
python -m chandra.scripts.run_api

# Opción 3: Con variables de entorno personalizadas
PORT=8080 HOST=0.0.0.0 chandra_api
```

Por defecto, el servidor se ejecuta en `http://localhost:5000`

## Endpoints

### 1. Health Check

**GET** `/api/health`

Verifica que el servidor esté funcionando.

**Respuesta:**
```json
{
  "status": "ok",
  "service": "chandra-ocr-api"
}
```

---

### 2. Procesar archivo (imagen o PDF)

**POST** `/api/ocr`

Procesa un archivo (imagen o PDF) y devuelve el texto extraído en formato Markdown, HTML y JSON.

**Parámetros (form-data):**

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `file` | file | Sí | - | Archivo a procesar (imagen o PDF) |
| `include_images` | string | No | "true" | Incluir imágenes extraídas: "true" o "false" |
| `include_headers_footers` | string | No | "false" | Incluir headers/footers: "true" o "false" |
| `max_output_tokens` | integer | No | - | Máximo de tokens de salida por página |
| `page_range` | string | No | - | Rango de páginas para PDFs (ej: "1-5,7,9-12") |

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/api/ocr \
  -F "file=@documento.pdf" \
  -F "include_images=true"
```

**Ejemplo con Python:**
```python
import requests

url = "http://localhost:5000/api/ocr"
files = {"file": open("documento.pdf", "rb")}
data = {
    "include_images": "true",
    "include_headers_footers": "false"
}

response = requests.post(url, files=files, data=data)
result = response.json()

print(result["markdown"])  # Texto en Markdown
print(result["html"])      # HTML estructurado
print(result["chunks"])    # Bloques con bbox y labels
```

**Respuesta:**
```json
{
  "markdown": "# Título\n\nContenido del documento...",
  "html": "<div>...</div>",
  "chunks": [
    {
      "bbox": [100, 200, 500, 300],
      "label": "Text",
      "content": "Contenido del bloque"
    }
  ],
  "images": {
    "image1.webp": "data:image/webp;base64,..."
  },
  "metadata": {
    "num_pages": 1,
    "total_token_count": 1234,
    "total_chunks": 10,
    "total_images": 2,
    "pages": [
      {
        "page_num": 1,
        "token_count": 1234,
        "num_chunks": 10,
        "num_images": 2,
        "page_box": [0, 0, 1920, 1080]
      }
    ],
    "include_images": true,
    "include_headers_footers": false
  }
}
```

---

### 3. Procesar imagen desde base64

**POST** `/api/ocr/image`

Procesa una imagen directamente desde una cadena base64 (útil para bots que reciben imágenes).

**Body (JSON):**

```json
{
  "image_base64": "data:image/png;base64,iVBORw0KGgo...",
  "include_images": true,
  "include_headers_footers": false,
  "max_output_tokens": 8192
}
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/api/ocr/image \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "data:image/png;base64,..."
  }'
```

**Ejemplo con Python:**
```python
import requests
import base64

# Leer imagen y convertir a base64
with open("imagen.png", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()
    image_data = f"data:image/png;base64,{image_base64}"

url = "http://localhost:5000/api/ocr/image"
payload = {
    "image_base64": image_data,
    "include_images": True
}

response = requests.post(url, json=payload)
result = response.json()

print(result["markdown"])
```

**Respuesta:** (igual que el endpoint `/api/ocr`)

---

## Ejemplo de integración con un bot (Telegram)

```python
from flask import Flask, request
import requests
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANDRA_API_URL = "http://localhost:5000/api/ocr/image"

app = Flask(__name__)

def process_image_with_chandra(image_url):
    """Descarga imagen y la procesa con Chandra"""
    import urllib.request
    import base64
    
    # Descargar imagen
    urllib.request.urlretrieve(image_url, "/tmp/image.jpg")
    
    # Convertir a base64
    with open("/tmp/image.jpg", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()
        image_data = f"data:image/jpeg;base64,{image_base64}"
    
    # Procesar con Chandra
    response = requests.post(
        CHANDRA_API_URL,
        json={"image_base64": image_data}
    )
    
    if response.status_code == 200:
        result = response.json()
        return result["markdown"]
    else:
        return f"Error: {response.json()}"

@app.route("/webhook", methods=["POST"])
def webhook():
    """Webhook de Telegram"""
    data = request.json
    
    if "message" in data and "photo" in data["message"]:
        # Obtener la foto más grande
        photo = data["message"]["photo"][-1]
        file_id = photo["file_id"]
        
        # Obtener URL del archivo
        file_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
        file_info = requests.get(file_url).json()
        file_path = file_info["result"]["file_path"]
        image_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        
        # Procesar imagen
        text = process_image_with_chandra(image_url)
        
        # Enviar respuesta
        chat_id = data["message"]["chat"]["id"]
        send_message_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(send_message_url, json={
            "chat_id": chat_id,
            "text": text[:4000]  # Limitar a 4000 caracteres
        })
    
    return "OK"

if __name__ == "__main__":
    app.run(port=3000)
```

---

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `PORT` | 5000 | Puerto del servidor |
| `HOST` | 0.0.0.0 | Host del servidor |
| `DEBUG` | false | Modo debug (true/false) |

---

## Notas

- El modelo se carga en memoria la primera vez que se usa (caché global)
- Asegúrate de tener el checkpoint descargado y una GPU configurada para acelerar la inferencia local
- Las imágenes extraídas se devuelven en formato base64 para facilitar el uso en APIs


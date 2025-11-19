# Exponer la API local a Internet para tu bot en fly.io

Para que tu bot en fly.io pueda acceder a la API que corre en tu PC, necesitas exponerla a internet usando un túnel.

## Opción 1: Cloudflare Tunnel (Recomendado - Gratis y permanente)

### 1. Instalar cloudflared

```bash
# Linux
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# O con snap
sudo snap install cloudflared
```

### 2. Autenticarse

```bash
cloudflared tunnel login
```

### 3. Crear un túnel

```bash
cloudflared tunnel create chandra-api
```

### 4. Configurar el túnel

Crea un archivo de configuración `~/.cloudflared/config.yml`:

```yaml
tunnel: <TUNNEL_ID>  # Lo obtienes del paso anterior
credentials-file: /home/<tu_usuario>/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: chandra-api.tu-dominio.com  # O usa un subdominio de cloudflare
    service: http://localhost:5000
  - service: http_status:404
```

### 5. Ejecutar el túnel

```bash
cloudflared tunnel run chandra-api
```

O como servicio:

```bash
sudo cloudflared service install
sudo systemctl start cloudflared
```

**URL pública:** `https://chandra-api.tu-dominio.com`

---

## Opción 2: ngrok (Rápido y fácil)

### 1. Instalar ngrok

```bash
# Descargar desde https://ngrok.com/download
# O con snap
sudo snap install ngrok
```

### 2. Registrarse y obtener token

1. Ve a https://ngrok.com y crea una cuenta
2. Obtén tu authtoken del dashboard

### 3. Configurar ngrok

```bash
ngrok config add-authtoken TU_AUTH_TOKEN
```

### 4. Iniciar el túnel

```bash
ngrok http 5000
```

Esto te dará una URL como: `https://abc123.ngrok-free.app`

**Nota:** La versión gratuita de ngrok cambia la URL cada vez que reinicias.

### 5. Para URL fija (requiere plan de pago)

```bash
ngrok http 5000 --domain=tu-dominio.ngrok-free.app
```

---

## Opción 3: localtunnel (Gratis, sin registro)

### 1. Instalar

```bash
npm install -g localtunnel
```

### 2. Iniciar túnel

```bash
lt --port 5000 --subdomain chandra-api
```

**URL:** `https://chandra-api.loca.lt`

**Nota:** Puede ser menos estable que las otras opciones.

---

## Opción 4: serveo.net (Sin instalación)

```bash
ssh -R 80:localhost:5000 serveo.net
```

**URL:** Te la dará en la salida del comando.

---

## Configurar tu bot en fly.io

Una vez que tengas la URL pública, actualiza tu bot:

```python
# En tu bot de fly.io
CHANDRA_API_URL = "https://chandra-api.tu-dominio.com"  # O la URL del túnel

# Usar la API
response = requests.post(
    f"{CHANDRA_API_URL}/api/ocr/image",
    json={"image_base64": image_data, "method": "vllm"}
)
```

---

## Script para iniciar todo automáticamente

Crea un script `start_api_with_tunnel.sh`:

```bash
#!/bin/bash

# Iniciar la API en segundo plano
cd /home/rodry/Desktop/chandra
source .venv/bin/activate
chandra_api &
API_PID=$!

# Esperar a que la API esté lista
sleep 3

# Iniciar el túnel (elige uno)
# Opción ngrok:
ngrok http 5000

# O con cloudflared:
# cloudflared tunnel run chandra-api

# Limpiar al salir
trap "kill $API_PID" EXIT
```

---

## Recomendación

Para producción, usa **Cloudflare Tunnel** porque:
- ✅ Es gratis
- ✅ URL permanente
- ✅ HTTPS automático
- ✅ Más estable
- ✅ Puedes usar tu propio dominio

Para desarrollo rápido, usa **ngrok** porque:
- ✅ Muy fácil de configurar
- ✅ No requiere dominio propio
- ✅ Perfecto para pruebas

---

## Verificar que funciona

```bash
# Desde tu PC
curl http://localhost:5000/api/health

# Desde internet (usa la URL del túnel)
curl https://tu-url-del-tunel/api/health
```


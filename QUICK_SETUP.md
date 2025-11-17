# Configuración Rápida de Cloudflare Tunnel

## ⚠️ Importante: NO uses "WARP Connector"

Si ves la opción "WARP Connector Linux distros only" en el dashboard de Cloudflare, **NO la uses**. Esa opción es para conectar redes completas, no para exponer servicios.

Para exponer tu API, usa la **línea de comandos** (más fácil y directo).

## 🚀 Pasos Rápidos

### 1. Autenticarse (abre el navegador automáticamente)

```bash
cd ~/Desktop/chandra
export PATH="$HOME/Desktop/chandra/bin:$PATH"
cloudflared tunnel login
```

Esto:
- Abrirá tu navegador
- Te pedirá que autorices cloudflared
- Descargará el certificado necesario

### 2. Crear el túnel

```bash
cloudflared tunnel create chandra-api
```

Te mostrará algo como:
```
Created tunnel chandra-api with id abc123def456...
```

**Guarda el ID** (lo necesitarás después).

### 3. Configurar DNS en Cloudflare Dashboard

1. Ve a https://dash.cloudflare.com
2. Selecciona tu dominio
3. Ve a **DNS** → **Records**
4. Haz clic en **Add record**
5. Configura:
   - **Type**: CNAME
   - **Name**: `chandra-api` (o el nombre que quieras)
   - **Target**: `<TUNNEL_ID>.cfargotunnel.com` (reemplaza con el ID del paso 2)
   - **Proxy status**: ☁️ **Proxied** (nube naranja - IMPORTANTE)
   - **TTL**: Auto
6. Guarda

**Ejemplo:**
- Si tu dominio es `midominio.com`
- Y el TUNNEL_ID es `abc123def456`
- El Target sería: `abc123def456.cfargotunnel.com`
- Tu API estará en: `https://chandra-api.midominio.com`

### 4. Crear archivo de configuración

```bash
nano ~/.cloudflared/config.yml
```

Pega esto (reemplaza los valores):

```yaml
tunnel: <TUNNEL_ID>
credentials-file: /home/rodry/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: chandra-api.<TU_DOMINIO>
    service: http://localhost:5000
  - service: http_status:404
```

**Ejemplo real:**
```yaml
tunnel: abc123def456
credentials-file: /home/rodry/.cloudflared/abc123def456.json

ingress:
  - hostname: chandra-api.midominio.com
    service: http://localhost:5000
  - service: http_status:404
```

**Nota:** El archivo `<TUNNEL_ID>.json` se crea automáticamente cuando ejecutas `cloudflared tunnel create`.

### 5. Iniciar todo

```bash
cd ~/Desktop/chandra
./start_with_cloudflare.sh
```

O manualmente en dos terminales:

**Terminal 1:**
```bash
cd ~/Desktop/chandra
source .venv/bin/activate
chandra_api
```

**Terminal 2:**
```bash
cd ~/Desktop/chandra
export PATH="$HOME/Desktop/chandra/bin:$PATH"
cloudflared tunnel run chandra-api
```

### 6. Verificar

Abre en tu navegador:
```
https://chandra-api.tu-dominio.com/api/health
```

Deberías ver:
```json
{"status":"ok","service":"chandra-ocr-api"}
```

## 📝 Resumen de Comandos

```bash
# 1. Agregar al PATH (en esta sesión)
export PATH="$HOME/Desktop/chandra/bin:$PATH"

# 2. Autenticarse
cloudflared tunnel login

# 3. Crear túnel
cloudflared tunnel create chandra-api

# 4. Configurar DNS en Cloudflare Dashboard (manual)

# 5. Crear config.yml
nano ~/.cloudflared/config.yml

# 6. Iniciar
./start_with_cloudflare.sh
```

## ❓ Preguntas Frecuentes

**P: ¿Debo usar el dashboard de Cloudflare?**
R: No es necesario. La línea de comandos es más fácil y directa.

**P: ¿Qué es WARP Connector?**
R: Es para conectar redes completas (como una VPN). No lo necesitas para exponer tu API.

**P: ¿Dónde encuentro el TUNNEL_ID?**
R: Se muestra cuando ejecutas `cloudflared tunnel create`, o puedes verlo con `cloudflared tunnel list`.

**P: ¿Cuánto cuesta?**
R: Es completamente gratis, incluso con tu propio dominio.

## 🐛 Problemas Comunes

**Error: "Cannot determine default origin certificate path"**
- Ejecuta primero: `cloudflared tunnel login`

**Error: "tunnel not found"**
- Verifica el nombre: `cloudflared tunnel list`
- Asegúrate de usar el mismo nombre en `config.yml`

**Error: "hostname not found"**
- Verifica que el DNS esté configurado
- Espera 1-2 minutos a que se propague
- Asegúrate de que el proxy esté activado (nube naranja)


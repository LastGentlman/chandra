# Configurar Cloudflare Tunnel para Chandra API

## ✅ Paso 1: Instalar cloudflared (Ya hecho)

cloudflared está instalado en `~/Desktop/chandra/bin/cloudflared`

## 📋 Paso 2: Autenticarse con Cloudflare

Ejecuta este comando (abrirá tu navegador):

```bash
cd ~/Desktop/chandra
export PATH="$HOME/Desktop/chandra/bin:$PATH"
cloudflared tunnel login
```

Esto:
1. Abrirá tu navegador
2. Te pedirá que autorices cloudflared
3. Guardará las credenciales en `~/.cloudflared/cert.pem`

## 🏗️ Paso 3: Crear el túnel

```bash
export PATH="$HOME/Desktop/chandra/bin:$PATH"
cloudflared tunnel create chandra-api
```

Esto creará un túnel llamado "chandra-api" y te mostrará el **TUNNEL_ID** (guárdalo).

## 🌐 Paso 4: Configurar DNS en Cloudflare Dashboard

1. Ve a https://dash.cloudflare.com
2. Selecciona tu dominio
3. Ve a **DNS** → **Records**
4. Haz clic en **Add record**
5. Configura:
   - **Type**: CNAME
   - **Name**: `chandra-api` (o el subdominio que quieras)
   - **Target**: `<TUNNEL_ID>.cfargotunnel.com` (reemplaza con tu TUNNEL_ID)
   - **Proxy status**: Proxied (nube naranja ☁️)
   - **TTL**: Auto
6. Guarda

**Ejemplo:**
- Si tu dominio es `midominio.com`
- Y creas el subdominio `chandra-api`
- Tu API estará en: `https://chandra-api.midominio.com`

## ⚙️ Paso 5: Configurar el archivo de configuración

Crea/edita el archivo `~/.cloudflared/config.yml`:

```bash
nano ~/.cloudflared/config.yml
```

Pega esto (reemplaza `<TUNNEL_ID>` y `<TU_DOMINIO>`):

```yaml
tunnel: <TUNNEL_ID>
credentials-file: /home/<TU_USUARIO>/.cloudflared/<TUNNEL_ID>.json

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

**Nota:** El archivo de credenciales se crea automáticamente cuando ejecutas `cloudflared tunnel create`.

## 🚀 Paso 6: Probar el túnel

```bash
cd ~/Desktop/chandra
export PATH="$HOME/Desktop/chandra/bin:$PATH"
./start_with_cloudflare.sh
```

O manualmente:

```bash
# Terminal 1: Iniciar la API
cd ~/Desktop/chandra
source .venv/bin/activate
chandra_api

# Terminal 2: Iniciar el túnel
export PATH="$HOME/Desktop/chandra/bin:$PATH"
cloudflared tunnel run chandra-api
```

## ✅ Paso 7: Verificar

Abre en tu navegador:
```
https://chandra-api.tu-dominio.com/api/health
```

Deberías ver:
```json
{"status":"ok","service":"chandra-ocr-api"}
```

## 🔄 Paso 8: Ejecutar como servicio (Opcional)

Para que el túnel se inicie automáticamente al reiniciar:

```bash
export PATH="$HOME/Desktop/chandra/bin:$PATH"
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

## 📝 Resumen de comandos

```bash
# Agregar cloudflared al PATH (en esta sesión)
export PATH="$HOME/Desktop/chandra/bin:$PATH"

# Autenticarse
cloudflared tunnel login

# Crear túnel
cloudflared tunnel create chandra-api

# Configurar DNS en Cloudflare Dashboard (manual)

# Editar config.yml
nano ~/.cloudflared/config.yml

# Ejecutar
./start_with_cloudflare.sh
```

## 🐛 Solución de problemas

### Error: "tunnel not found"
- Verifica que el nombre del túnel sea correcto
- Lista tus túneles: `cloudflared tunnel list`

### Error: "credentials file not found"
- Verifica la ruta en `config.yml`
- El archivo debería estar en `~/.cloudflared/<TUNNEL_ID>.json`

### Error: "hostname not found"
- Verifica que el DNS esté configurado correctamente
- Espera unos minutos a que se propague el DNS
- Verifica que el proxy esté activado (nube naranja)

### El túnel se desconecta
- Verifica que la API esté corriendo en `localhost:5000`
- Revisa los logs: `cloudflared tunnel run chandra-api --loglevel debug`


# Comandos Útiles - Chandra OCR API

## 🚀 Iniciar el servidor (API + Cloudflare Tunnel)

```bash
cd ~/Desktop/chandra
./start_with_cloudflare.sh
```

Este comando:
- ✅ Inicia la API en `localhost:5000`
- ✅ Inicia el túnel de Cloudflare
- ✅ Expone tu API públicamente en `https://chandra-api.tu-dominio.com`

**Nota:** Mantén esta terminal abierta mientras quieras que el servidor esté activo.

---

## 🛑 Detener el servidor

Presiona `Ctrl+C` en la terminal donde está corriendo el script.

O manualmente:
```bash
pkill -f chandra_api
pkill -f cloudflared
```

---

## 📊 Verificar estado

### Ver si está corriendo:
```bash
ps aux | grep -E "chandra_api|cloudflared" | grep -v grep
```

### Verificar la API local:
```bash
curl http://localhost:5000/api/health
```

### Verificar la API pública:
```bash
curl https://chandra-api.tu-dominio.com/api/health
```

---

## 🔍 Ver logs

### Logs de la API:
```bash
tail -f /tmp/chandra_api.log
```

### Logs del túnel:
Los logs del túnel aparecen en la terminal donde ejecutaste el script.

---

## 🔄 Reiniciar el servidor

```bash
# Detener
pkill -f chandra_api
pkill -f cloudflared

# Iniciar de nuevo
./start_with_cloudflare.sh
```

---

## ⚙️ Solo iniciar la API (sin túnel)

Si solo quieres la API local:

```bash
cd ~/Desktop/chandra
source .venv/bin/activate
chandra_api
```

---

## 🌐 Solo iniciar el túnel (si la API ya está corriendo)

```bash
cd ~/Desktop/chandra
export PATH="$HOME/Desktop/chandra/bin:$PATH"
cloudflared tunnel run chandra-api
```

---

## 📝 Resumen

**Para uso diario:**
```bash
cd ~/Desktop/chandra
./start_with_cloudflare.sh
```

**Para detener:**
- Presiona `Ctrl+C` en la terminal

**Para verificar:**
```bash
curl https://chandra-api.tu-dominio.com/api/health
```

---

## 💡 Tips

1. **Mantén la terminal abierta:** El script necesita estar corriendo para que el servidor funcione.

2. **Si se cierra la terminal:** El servidor se detendrá. Para que corra en segundo plano, puedes usar `screen` o `tmux`:
   ```bash
   screen -S chandra
   ./start_with_cloudflare.sh
   # Presiona Ctrl+A luego D para desconectar
   # Para reconectar: screen -r chandra
   ```

3. **Para iniciar automáticamente al arrancar:** Configura el túnel como servicio (ver SETUP_CLOUDFLARE.md).

4. **URL de tu API:** Una vez configurado, tu API estará siempre en:
   ```
   https://chandra-api.tu-dominio.com
   ```


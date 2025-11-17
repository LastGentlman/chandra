#!/bin/bash
# Script para instalar cloudflared

echo "📥 Instalando cloudflared..."

# Crear directorio bin si no existe
mkdir -p ~/Desktop/chandra/bin
cd ~/Desktop/chandra/bin

# Descargar cloudflared
echo "⬇️  Descargando cloudflared..."
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared

# Hacer ejecutable
chmod +x cloudflared

# Verificar instalación
if ./cloudflared --version > /dev/null 2>&1; then
    echo "✅ cloudflared instalado correctamente"
    ./cloudflared --version
    
    # Agregar al PATH si no está
    if ! echo $PATH | grep -q "chandra/bin"; then
        echo ""
        echo "📝 Agregando al PATH..."
        echo 'export PATH="$HOME/Desktop/chandra/bin:$PATH"' >> ~/.bashrc
        export PATH="$HOME/Desktop/chandra/bin:$PATH"
        echo "✅ Agregado al PATH (recarga tu terminal o ejecuta: source ~/.bashrc)"
    fi
    
    echo ""
    echo "🎉 Instalación completada!"
    echo "Ejecuta: cloudflared --version para verificar"
else
    echo "❌ Error en la instalación"
    exit 1
fi


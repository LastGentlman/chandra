import os
import sys


def main():
    """Ejecuta la API REST de Chandra OCR"""
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    api_path = os.path.join(cur_dir, "api.py")
    
    # Importar y ejecutar la app
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(cur_dir))))
    
    from chandra.scripts.api import app
    
    # Configuración del servidor
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    print(f"Starting Chandra OCR API on {host}:{port}")
    print(f"Endpoints:")
    print(f"  - POST /api/ocr - Procesar archivo (imagen o PDF)")
    print(f"  - POST /api/ocr/image - Procesar imagen desde base64")
    print(f"  - GET /api/health - Health check")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()


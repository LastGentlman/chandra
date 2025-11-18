"""
API REST para Chandra OCR
Permite procesar imágenes y PDFs mediante endpoints HTTP
"""
import base64
import io
import json
import os
from pathlib import Path
from typing import Optional

from flask import Flask, request, jsonify
from PIL import Image
import filetype

from chandra.model import InferenceManager
from chandra.model.schema import BatchInputItem
from chandra.input import load_file
from chandra.settings import settings


app = Flask(__name__)

# Variable global para el modelo (se inicializa en el primer uso)
_model_cache = {}


# Configurar CORS para permitir acceso desde cualquier origen
@app.after_request
def after_request(response):
    """Agrega headers CORS a todas las respuestas"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


def verify_api_key():
    """Verifica la API key si está habilitada"""
    # No verificar en health check ni en preflight
    if request.endpoint == 'health' or request.method == "OPTIONS":
        return None
    
    # Si no se requiere API key, permitir acceso
    if not settings.CHANDRA_REQUIRE_API_KEY:
        return None
    
    # Si se requiere pero no está configurada, permitir acceso (modo desarrollo)
    if not settings.CHANDRA_API_KEY:
        return None
    
    # Obtener API key del header Authorization o del parámetro api_key
    api_key = None
    
    # Intentar desde header Authorization (formato: Bearer <key> o <key>)
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        api_key = auth_header[7:].strip()
    elif auth_header:
        api_key = auth_header.strip()
    
    # Si no está en el header, intentar desde parámetros (query string o form-data)
    if not api_key:
        api_key = request.args.get('api_key') or request.form.get('api_key')
    
    # Si es JSON, también verificar en el body
    if not api_key and request.is_json:
        data = request.get_json(silent=True)
        if data and 'api_key' in data:
            api_key = data['api_key']
    
    # Verificar la clave
    if not api_key or api_key != settings.CHANDRA_API_KEY:
        return jsonify({"error": "Invalid or missing API key"}), 401
    
    return None


@app.before_request
def handle_preflight():
    """Maneja las peticiones OPTIONS (preflight) de CORS"""
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    # Verificar API key antes de procesar la petición
    api_key_error = verify_api_key()
    if api_key_error:
        return api_key_error


def get_model(method: str = "vllm") -> InferenceManager:
    """Obtiene o crea el modelo de inferencia (con caché)"""
    if method not in _model_cache:
        _model_cache[method] = InferenceManager(method=method)
    return _model_cache[method]


def image_to_base64(pil_image: Image.Image, format: str = "PNG") -> str:
    """Convierte una imagen PIL a base64"""
    buffered = io.BytesIO()
    pil_image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/{format.lower()};base64,{img_str}"


def process_images_to_base64(images_dict: dict) -> dict:
    """Convierte todas las imágenes del diccionario a base64"""
    return {
        name: image_to_base64(img) 
        for name, img in images_dict.items()
    }


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "chandra-ocr-api"})


@app.route("/api/ocr", methods=["POST"])
def ocr():
    """
    Endpoint principal para procesar OCR
    
    Parámetros (form-data):
    - file: archivo (imagen o PDF)
    - method: "hf" o "vllm" (default: "vllm")
    - include_images: "true" o "false" (default: "true")
    - include_headers_footers: "true" o "false" (default: "false")
    - max_output_tokens: número entero (opcional)
    - page_range: rango de páginas para PDFs, ej: "1-5,7,9-12" (opcional)
    
    Retorna JSON con:
    - markdown: texto en formato markdown
    - html: HTML estructurado
    - chunks: lista de bloques con bbox y labels
    - images: diccionario de imágenes extraídas (en base64)
    - metadata: información sobre el procesamiento
    """
    try:
        # Verificar que hay un archivo
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        # Obtener parámetros opcionales
        method = request.form.get("method", "vllm").lower()
        if method not in ["hf", "vllm"]:
            return jsonify({"error": "method must be 'hf' or 'vllm'"}), 400

        include_images = request.form.get("include_images", "true").lower() == "true"
        include_headers_footers = request.form.get("include_headers_footers", "false").lower() == "true"
        
        max_output_tokens = request.form.get("max_output_tokens")
        if max_output_tokens:
            try:
                max_output_tokens = int(max_output_tokens)
            except ValueError:
                return jsonify({"error": "max_output_tokens must be an integer"}), 400
        
        page_range = request.form.get("page_range", None)

        # Guardar archivo temporalmente
        temp_path = Path("/tmp") / file.filename
        file.save(str(temp_path))

        try:
            # Cargar imágenes del archivo
            config = {"page_range": page_range} if page_range else {}
            images = load_file(str(temp_path), config)
            
            if not images:
                return jsonify({"error": "No images could be loaded from file"}), 400

            # Obtener modelo
            model = get_model(method)

            # Procesar todas las páginas
            all_results = []
            for img in images:
                batch = [BatchInputItem(image=img, prompt_type="ocr_layout")]
                
                generate_kwargs = {
                    "include_images": include_images,
                    "include_headers_footers": include_headers_footers,
                }
                
                if max_output_tokens:
                    generate_kwargs["max_output_tokens"] = max_output_tokens

                results = model.generate(batch, **generate_kwargs)
                all_results.extend(results)

            # Combinar resultados de múltiples páginas
            combined_markdown = []
            combined_html = []
            all_chunks = []
            all_extracted_images = {}
            total_tokens = 0
            page_metadata = []

            for page_num, result in enumerate(all_results):
                combined_markdown.append(result.markdown)
                combined_html.append(result.html)
                all_chunks.extend(result.chunks)
                
                # Combinar imágenes extraídas
                for img_name, img in result.images.items():
                    # Agregar prefijo de página si hay múltiples páginas
                    if len(all_results) > 1:
                        img_name = f"page_{page_num + 1}_{img_name}"
                    all_extracted_images[img_name] = img
                
                total_tokens += result.token_count
                
                page_metadata.append({
                    "page_num": page_num + 1,
                    "token_count": result.token_count,
                    "num_chunks": len(result.chunks),
                    "num_images": len(result.images),
                    "page_box": result.page_box,
                })

            # Convertir imágenes a base64 para la respuesta JSON
            images_base64 = process_images_to_base64(all_extracted_images) if include_images else {}

            # Preparar respuesta
            response = {
                "markdown": "\n\n".join(combined_markdown),
                "html": "\n\n".join(combined_html),
                "chunks": all_chunks,
                "images": images_base64,
                "metadata": {
                    "num_pages": len(all_results),
                    "total_token_count": total_tokens,
                    "total_chunks": len(all_chunks),
                    "total_images": len(all_extracted_images),
                    "pages": page_metadata,
                    "method": method,
                    "include_images": include_images,
                    "include_headers_footers": include_headers_footers,
                }
            }

            return jsonify(response)

        finally:
            # Limpiar archivo temporal
            if temp_path.exists():
                temp_path.unlink()

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ocr/image", methods=["POST"])
def ocr_image():
    """
    Endpoint simplificado para procesar una imagen directamente desde base64
    
    Body JSON:
    {
        "image_base64": "data:image/png;base64,...",
        "method": "vllm",
        "include_images": true,
        "include_headers_footers": false
    }
    """
    try:
        data = request.get_json()
        if not data or "image_base64" not in data:
            return jsonify({"error": "image_base64 is required"}), 400

        # Decodificar imagen base64
        image_data = data["image_base64"]
        if image_data.startswith("data:image"):
            # Remover el prefijo data:image/...;base64,
            image_data = image_data.split(",")[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Obtener parámetros
        method = data.get("method", "vllm").lower()
        include_images = data.get("include_images", True)
        include_headers_footers = data.get("include_headers_footers", False)
        max_output_tokens = data.get("max_output_tokens")

        # Obtener modelo
        model = get_model(method)

        # Procesar
        batch = [BatchInputItem(image=image, prompt_type="ocr_layout")]
        
        generate_kwargs = {
            "include_images": include_images,
            "include_headers_footers": include_headers_footers,
        }
        
        if max_output_tokens:
            generate_kwargs["max_output_tokens"] = max_output_tokens

        results = model.generate(batch, **generate_kwargs)
        result = results[0]

        # Convertir imágenes a base64
        images_base64 = process_images_to_base64(result.images) if include_images else {}

        response = {
            "markdown": result.markdown,
            "html": result.html,
            "chunks": result.chunks,
            "images": images_base64,
            "metadata": {
                "token_count": result.token_count,
                "num_chunks": len(result.chunks),
                "num_images": len(result.images),
                "page_box": result.page_box,
                "method": method,
            }
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Configuración del servidor
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    print(f"Starting Chandra OCR API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


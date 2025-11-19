"""
Ejemplo de integración de Chandra OCR API con un bot
Este ejemplo muestra cómo usar la API desde Python
"""
import requests
import base64
from pathlib import Path


# URL de la API (ajusta según tu configuración)
API_URL = "http://localhost:5000"


def process_file(file_path: str) -> dict:
    """
    Procesa un archivo (imagen o PDF) usando la API de Chandra
    
    Args:
        file_path: Ruta al archivo a procesar
    
    Returns:
        Diccionario con los resultados (markdown, html, chunks, etc.)
    """
    url = f"{API_URL}/api/ocr"
    
    with open(file_path, "rb") as f:
        files = {"file": (Path(file_path).name, f, "application/octet-stream")}
        data = {
            "include_images": "true",
            "include_headers_footers": "false"
        }
        
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        
        return response.json()


def process_image_base64(image_base64: str) -> dict:
    """
    Procesa una imagen desde base64 usando la API de Chandra
    
    Args:
        image_base64: Imagen en formato base64 (con o sin prefijo data:image/...)
    
    Returns:
        Diccionario con los resultados
    """
    url = f"{API_URL}/api/ocr/image"
    
    # Asegurar que tiene el prefijo data:image
    if not image_base64.startswith("data:image"):
        image_base64 = f"data:image/png;base64,{image_base64}"
    
    payload = {
        "image_base64": image_base64,
        "include_images": True,
        "include_headers_footers": False
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    return response.json()


def process_image_file(image_path: str) -> dict:
    """
    Procesa un archivo de imagen convirtiéndolo a base64 primero
    
    Args:
        image_path: Ruta al archivo de imagen
    
    Returns:
        Diccionario con los resultados
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode()
        
        # Detectar tipo de imagen
        ext = Path(image_path).suffix.lower()
        mime_type = {
            ".png": "png",
            ".jpg": "jpeg",
            ".jpeg": "jpeg",
            ".gif": "gif",
            ".webp": "webp"
        }.get(ext, "png")
        
        image_data = f"data:image/{mime_type};base64,{image_base64}"
        
        return process_image_base64(image_data)


# Ejemplo de uso
if __name__ == "__main__":
    # Verificar que la API está funcionando
    try:
        health_response = requests.get(f"{API_URL}/api/health")
        print(f"API Status: {health_response.json()}")
    except Exception as e:
        print(f"Error conectando a la API: {e}")
        print("Asegúrate de que el servidor esté corriendo con: chandra_api")
        exit(1)
    
    # Ejemplo 1: Procesar un archivo
    print("\n=== Ejemplo 1: Procesar archivo ===")
    # Descomenta y ajusta la ruta a tu archivo
    # result = process_file("ejemplo.pdf")
    # print(f"Markdown:\n{result['markdown'][:500]}...")
    # print(f"\nMetadata: {result['metadata']}")
    
    # Ejemplo 2: Procesar imagen desde archivo
    print("\n=== Ejemplo 2: Procesar imagen ===")
    # Descomenta y ajusta la ruta a tu imagen
    # result = process_image_file("ejemplo.png")
    # print(f"Markdown:\n{result['markdown'][:500]}...")
    # print(f"\nChunks encontrados: {len(result['chunks'])}")
    
    print("\n✅ Ejemplos listos. Descomenta las líneas para probar con tus archivos.")


import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin

# Ruta absoluta al directorio del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "notas_json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://www.cuartopoder.mx"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def obtener_links_de_noticias():
    """Obtiene links de las últimas 10 noticias desde la página principal."""
    print("🔍 Conectando a la página principal...")
    resp = requests.get(BASE_URL, headers=HEADERS)
    if resp.status_code != 200:
        print(f"❌ Error al acceder a la página: {resp.status_code}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    links = []

    print("🔎 Buscando noticias...")
    articulos = soup.select("div.post-details h2.entry-title a")
    print(f"🔗 Se encontraron {len(articulos)} enlaces de artículos.")

    for a in articulos[:10]:
        url = a.get('href')
        if url:
            full_url = urljoin(BASE_URL, url)
            print(f"✅ Noticia encontrada: {full_url}")
            links.append(full_url)

    return links

def extraer_info_noticia(url):
    """Extrae la información estructurada de una noticia individual."""
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        raise Exception(f"No se pudo acceder a la nota: {resp.status_code}")

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Título
    titulo_elem = soup.find("h1", class_="entry-title")
    titulo = titulo_elem.get_text(strip=True) if titulo_elem else "Sin título"

    # Fecha
    fecha_elem = soup.find("time", class_="entry-date")
    fecha = fecha_elem.get_text(strip=True) if fecha_elem else "Sin fecha"

    # Contenido
    parrafos = soup.select("div.entry-content > p")
    lugar = parrafos[0].get_text(strip=True) if parrafos else "No especificado"
    contenido = "\n".join([p.get_text(strip=True) for p in parrafos]) if parrafos else "Sin contenido"

    return {
        "titulo": titulo,
        "fecha": fecha,
        "lugar_de_los_hechos": lugar,
        "contenido_completo": contenido,
        "url": url
    }

def guardar_noticia_como_json(data, index):
    """Guarda una nota en un archivo JSON."""
    nombre_archivo = os.path.join(OUTPUT_DIR, f"noticia_{index + 1}.json")
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"💾 Guardada: {nombre_archivo}")

def main():
    links = obtener_links_de_noticias()
    if not links:
        print("⚠️ No se encontraron noticias. Revisa el selector CSS o el contenido cargado por JavaScript.")
        return

    for idx, url in enumerate(links):
        try:
            print(f"\n➡️ Procesando noticia {idx + 1}")
            nota = extraer_info_noticia(url)
            guardar_noticia_como_json(nota, idx)
        except Exception as e:
            print(f"❌ Error procesando {url}: {e}")

if __name__ == "__main__":
    main()

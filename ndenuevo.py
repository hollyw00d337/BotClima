from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
import re
from urllib.parse import urlparse

# Configuración headless
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

# Visitar la portada
url = "https://www.cuartopoder.mx"
driver.get(url)
time.sleep(3)
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Extrae titulares y URLs
def extraer_titulares(soup):
    noticias = []
    for a in soup.find_all("a", href=True):
        texto = a.get_text(strip=True)
        href = a["href"]
        if (
            texto and len(texto.split()) > 4
            and href.startswith("/")
            and not href.endswith("/")
            and not re.search(r"^(ir a sección|sube tu foto)", texto, re.I)
        ):
            noticias.append({
                "titulo": texto,
                "url": "https://www.cuartopoder.mx" + href
            })
    return noticias

titulares = extraer_titulares(soup)

# Extrae contenido, fecha y sección
def procesar_nota(url):
    driver.get(url)
    time.sleep(2)
    soup_n = BeautifulSoup(driver.page_source, 'html.parser')

    # Probar varios posibles selectores de contenido
    contenido = ""
    for sel in ["div.entry-content", "div.content", "div.jl_article_content", "article .contenido"]:
        cont_div = soup_n.select_one(sel)
        if cont_div:
            contenido = "\n".join(p.get_text(strip=True) for p in cont_div.find_all("p"))
            break  # si encuentra uno válido, ya no sigue

    if not contenido:
        print(f"⚠️ No se detectó contenido en {url}. Mostrando HTML parcial para inspección:")
        snippet = soup_n.get_text()[:200]
        print(snippet)

    # Extraer fecha con varios posibles selectores
    fecha = ""
    for sel in ["time[datetime]", "span.post-date", "div.jl_article_date", "div.date"]:
        f = soup_n.select_one(sel)
        if f:
            fecha = f.get_text(strip=True)
            break

    # Sección vía URL
    seccion = urlparse(url).path.strip("/").split("/")[0] or ""

    return contenido, fecha, seccion

notas = []
for i, t in enumerate(titulares, start=1):
    print(f"🔍 ({i}/{len(titulares)}) Procesando: {t['titulo']}")
    contenido, fecha, seccion = procesar_nota(t["url"])
    if contenido:
        notas.append({
            "titulo": t["titulo"],
            "url": t["url"],
            "fecha": fecha,
            "seccion": seccion,
            "contenido": contenido
        })

driver.quit()

# Guardar JSON
with open("noticias_mongodb.json", "w", encoding="utf-8") as f:
    json.dump(notas, f, ensure_ascii=False, indent=2)

print(f"\n✅ {len(notas)} noticias guardadas en 'noticias_mongodb.json'")

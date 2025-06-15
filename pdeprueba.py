import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
import csv
from selenium.webdriver.chrome.options import Options
import psycopg2
import pandas as pd

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-dev-shm-usage")


# ---------- Configuración del WebDriver (headless) ----------
def crear_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    return webdriver.Chrome(options=options)

# ---------- Scrapers personalizados ----------
def scraper_cuarto_poder(soup):
    return extraer_por_id(soup, "tab1popular", "Lo Más Leído") + \
           extraer_por_id(soup, "tab2popular", "Lo Último")

def scraper_diario_chiapas(soup):
    resultados = []
    # Lo Último
    ultimos = soup.select("div.jeg_posts article")[:5]
    for i, art in enumerate(ultimos, 1):
        link = art.find("a")
        if link:
            resultados.append({
                "ranking": i,
                "titulo": link.get_text(strip=True),
                "url": link['href'],
                "tipo": "Lo Último"
            })
    return resultados

def scraper_alerta_chiapas(soup):
    resultados = []
    # Lo Último
    ultimos = soup.select("div.td-module-thumb a")[:5]
    for i, link in enumerate(ultimos, 1):
        if link:
            resultados.append({
                "ranking": i,
                "titulo": link.get("title", link.get_text(strip=True)),
                "url": link['href'],
                "tipo": "Lo Último"
            })
    return resultados
# Scrapers vacíos con estructura preparada
def scraper_lajornada(driver, url):
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    resultados = []

    # === A PERSONALIZAR: Lo Último ===
    ultimos = soup.select("div.lo-ultimo-selector")  # Reemplazar con selector real
    for i, item in enumerate(ultimos[:5], 1):
        link = item.find("a")
        if link:
            resultados.append({
                "ranking": i,
                "titulo": link.get_text(strip=True),
                "url": link["href"],
                "tipo": "Lo Último",
                "sitio": "www.jornada.com.mx",
                "nivel": "Nivel 2"
            })

    # === A PERSONALIZAR: Lo Más Leído ===
    mas_leido = soup.select("div.mas-leido-selector")  # Reemplazar con selector real
    for i, item in enumerate(mas_leido[:5], 1):
        link = item.find("a")
        if link:
            resultados.append({
                "ranking": i,
                "titulo": link.get_text(strip=True),
                "url": link["href"],
                "tipo": "Lo Más Leído",
                "sitio": "www.jornada.com.mx",
                "nivel": "Nivel 2"
            })

    return resultados


def scraper_eluniversal(driver, url):
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    resultados = []

    # A PERSONALIZAR
    ultimos = soup.select("div.ultimas-noticias")  # Reemplazar con selector real
    for i, item in enumerate(ultimos[:5], 1):
        link = item.find("a")
        if link:
            resultados.append({
                "ranking": i,
                "titulo": link.get_text(strip=True),
                "url": link["href"],
                "tipo": "Lo Último",
                "sitio": "www.eluniversal.com.mx",
                "nivel": "Nivel 2"
            })

    mas_leido = soup.select("div.mas-leido")  # Reemplazar con selector real
    for i, item in enumerate(mas_leido[:5], 1):
        link = item.find("a")
        if link:
            resultados.append({
                "ranking": i,
                "titulo": link.get_text(strip=True),
                "url": link["href"],
                "tipo": "Lo Más Leído",
                "sitio": "www.eluniversal.com.mx",
                "nivel": "Nivel 2"
            })

    return resultados


def scraper_elpais(driver, url):
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    resultados = []

    ultimos = soup.select("div.lo-ultimo")  # A PERSONALIZAR
    for i, item in enumerate(ultimos[:5], 1):
        link = item.find("a")
        if link:
            resultados.append({
                "ranking": i,
                "titulo": link.get_text(strip=True),
                "url": link["href"],
                "tipo": "Lo Último",
                "sitio": "elpais.com",
                "nivel": "Nivel 3"
            })

    mas_leido = soup.select("div.destacado")  # A PERSONALIZAR
    for i, item in enumerate(mas_leido[:5], 1):
        link = item.find("a")
        if link:
            resultados.append({
                "ranking": i,
                "titulo": link.get_text(strip=True),
                "url": link["href"],
                "tipo": "Lo Más Leído",
                "sitio": "elpais.com",
                "nivel": "Nivel 3"
            })

    return resultados


def scraper_cnn(driver, url):
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    resultados = []

    ultimos = soup.select("div.noticia-reciente")  # A PERSONALIZAR
    for i, item in enumerate(ultimos[:5], 1):
        link = item.find("a")
        if link:
            resultados.append({
                "ranking": i,
                "titulo": link.get_text(strip=True),
                "url": link["href"],
                "tipo": "Lo Último",
                "sitio": "cnnespanol.cnn.com",
                "nivel": "Nivel 3"
            })

    mas_leido = soup.select("div.populares")  # A PERSONALIZAR
    for i, item in enumerate(mas_leido[:5], 1):
        link = item.find("a")
        if link:
            resultados.append({
                "ranking": i,
                "titulo": link.get_text(strip=True),
                "url": link["href"],
                "tipo": "Lo Más Leído",
                "sitio": "cnnespanol.cnn.com",
                "nivel": "Nivel 3"
            })

    return resultados
# ---------- Extraer por ID genérico (usado por CuartoPoder) ----------
def extraer_por_id(soup, div_id, tipo):
    resultados = []
    seccion = soup.select_one(f"div#{div_id}")
    if seccion:
        titulares = seccion.select("div.jl_m_right")[:5]
        for i, item in enumerate(titulares, 1):
            link = item.find("a")
            if link:
                resultados.append({
                    "ranking": i,
                    "titulo": link.get_text(strip=True),
                    "url": "https://www.cuartopoder.mx" + link['href'],
                    "tipo": tipo
                })
    return resultados
# ---------- Cargar URLs desde archivo ----------
def cargar_urls(nombre_archivo):
    with open(nombre_archivo, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# ---------- Ejecutar scraping por nivel ----------
def procesar_nivel(nombre_archivo, nivel_nombre, salida_csv):
    urls = cargar_urls(nombre_archivo)
    driver = crear_driver()
    todos_los_datos = []

    for url in urls:
        print(f"🔍 Procesando: {url}")
        try:
            driver.get(url)
            time.sleep(3)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            dominio = urlparse(url).netloc

            if dominio in scrapers:
                datos = scrapers[dominio](soup)
                for d in datos:
                    d['sitio'] = dominio
                    d['nivel'] = nivel_nombre
                todos_los_datos.extend(datos)
            else:
                print(f"⚠️ No hay scraper definido para: {dominio}")
        except Exception as e:
            print(f"❌ Error procesando {url}: {e}")

    driver.quit()
    df = pd.DataFrame(todos_los_datos)
    df.to_csv(salida_csv, index=False)
    print(f"✅ Datos guardados en {salida_csv}\n")
""""
def extraer_noticia_generico(driver, url, sitio, nivel):
    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Placeholder generales (ajustables por sitio)
    autor = soup.find("span", class_="autor") or soup.find("p", class_="author")
    fecha = soup.find("time") or soup.find("span", class_="fecha")
    titulo = soup.find("h1")
    cuerpo = soup.find("div", class_="article-body") or soup.find("div", class_="entry-content")

    return {
        "autor": autor.get_text(strip=True) if autor else "No disponible",
        "fecha": fecha.get_text(strip=True) if fecha else "No disponible",
        "titulo": titulo.get_text(strip=True) if titulo else "No disponible",
        "sitio": sitio,
        "cuerpo": cuerpo.get_text(strip=True) if cuerpo else "No disponible",
        "nivel": nivel
    }"""
def extraer_noticia_diariodechiapas(driver, url, nivel):
    from bs4 import BeautifulSoup
    import time

    driver.get(url)
    time.sleep(2)  # Esperar a que cargue completamente

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Título
    titulo_tag = soup.find("h1", class_="entry-title")
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else "No disponible"

    # Fecha
    fecha_tag = soup.find("time", class_="entry-date")
    fecha = fecha_tag.get_text(strip=True) if fecha_tag else "No disponible"

    # Autor (no visible en muchas noticias de este sitio)
    autor = "No disponible"

    # Cuerpo de la noticia
    cuerpo_tag = soup.find("div", class_="td-post-content")
    cuerpo = cuerpo_tag.get_text(separator="\n", strip=True) if cuerpo_tag else "No disponible"

    return {
        "autor": autor,
        "fecha": fecha,
        "titulo": titulo,
        "sitio": "diariodechiapas.com",
        "cuerpo": cuerpo,
        "nivel": nivel
    }

def insertar_en_postgre(datos, nivel):
    tabla = f"nivel{nivel}"

    conn = psycopg2.connect(
        dbname="noticias",
        user="postgres",  # Cambia si tu usuario es distinto
        password="TU_CONTRASEÑA",  # Sustituye con tu contraseña real
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    for _, fila in datos.iterrows():
        try:
            cur.execute(
                f"""
                INSERT INTO {tabla} (ranking, titulo, url, tipo, sitio, nivel)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
                """,
                (fila['ranking'], fila['titulo'], fila['url'], fila['tipo'], fila['sitio'], fila['nivel'])
            )
        except Exception as e:
            print(f"Error insertando {fila['url']}: {e}")

    conn.commit()
    cur.close()
    conn.close()

# ---------- Función para procesar nivel ----------
def procesar_nivel(archivo_txt, nombre_nivel, archivo_salida_csv):
    # Esta función debe incluir el código para obtener las noticias de cada archivo .txt,
    # ya lo debes tener configurado con tus scrapers de nivel1, nivel2, nivel3
    # Aquí asumimos que se genera un DataFrame `df_resultados` con las columnas requeridas:
    # ['ranking', 'titulo', 'url', 'tipo', 'sitio', 'nivel']

    # Simulación (placeholder), reemplaza esto por el scraping real
    df_resultados = pd.DataFrame([
        {'ranking': 1, 'titulo': 'Ejemplo 1', 'url': 'http://ejemplo1.com', 'tipo': 'destacado', 'sitio': 'ejemplo.com', 'nivel': nombre_nivel},
        {'ranking': 2, 'titulo': 'Ejemplo 2', 'url': 'http://ejemplo2.com', 'tipo': 'reciente', 'sitio': 'ejemplo.com', 'nivel': nombre_nivel}
    ])
    
    df_resultados.to_csv(archivo_salida_csv, index=False)
# ---------- Registro de scrapers por dominio ----------
scrapers = {
    "www.cuartopoder.mx": scraper_cuarto_poder,
    "diariodechiapas.com": scraper_diario_chiapas,
    "alertachiapas.com": scraper_alerta_chiapas,
    #'cuartopoder.mx': extraer_noticia_cuartopoder,
    'diariodechiapas.com': extraer_noticia_diariodechiapas
    #'alertachiapas.com': extraer_noticia_alertachiapas,
    #'www.jornada.com.mx': extraer_noticia_lajornada,
    #'www.eluniversal.com.mx': extraer_noticia_eluniversal,
    #'elpais.com': extraer_noticia_elpais,
    #'cnnespanol.cnn.com': extraer_noticia_cnn
}
scrapers_nivel2 = {
    "www.jornada.com.mx": scraper_lajornada,
    "www.eluniversal.com.mx": scraper_eluniversal,
}

scrapers_nivel3 = {
    "elpais.com": scraper_elpais,
    "cnnespanol.cnn.com": scraper_cnn,
}
#Insertar Postgre
def insertar_en_postgre(datos, nivel):
    tabla = f"nivel{nivel}"

    conn = psycopg2.connect(
        dbname="noticias",
        user="eduardomendoza",
        password="1234",  # Reemplaza con la contraseña correcta
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    for _, fila in datos.iterrows():
        try:
            cur.execute(
                f"""
                INSERT INTO {tabla} (ranking, titulo, url, tipo, sitio, nivel)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
                """,
                (fila['ranking'], fila['titulo'], fila['url'], fila['tipo'], fila['sitio'], fila['nivel'])
            )
        except Exception as e:
            print(f"Error insertando {fila['url']}: {e}")

    conn.commit()
    cur.close()
    conn.close()

# ---------- Función para procesar nivel ----------
def procesar_nivel(archivo_txt, nombre_nivel, archivo_salida_csv):
    # Esta función debe incluir el código para obtener las noticias de cada archivo .txt,
    # ya lo debes tener configurado con tus scrapers de nivel1, nivel2, nivel3
    # Aquí asumimos que se genera un DataFrame `df_resultados` con las columnas requeridas:
    # ['ranking', 'titulo', 'url', 'tipo', 'sitio', 'nivel']

    # Simulación (placeholder), reemplaza esto por el scraping real
    df_resultados = pd.DataFrame([
        {'ranking': 1, 'titulo': 'Ejemplo 1', 'url': 'http://ejemplo1.com', 'tipo': 'destacado', 'sitio': 'ejemplo.com', 'nivel': nombre_nivel},
        {'ranking': 2, 'titulo': 'Ejemplo 2', 'url': 'http://ejemplo2.com', 'tipo': 'reciente', 'sitio': 'ejemplo.com', 'nivel': nombre_nivel}
    ])
    
    df_resultados.to_csv(archivo_salida_csv, index=False)

# ---------- Ejecutar ----------
if __name__ == "__main__":
    procesar_nivel("nivel1.txt", "Nivel 1", "nivel1_resultados.csv")
    # Puedes agregar otros niveles:
    procesar_nivel("nivel2.txt", "Nivel 2", "nivel2_resultados.csv")
    procesar_nivel("nivel3.txt", "Nivel 3", "nivel3_resultados.csv")
    #procesar_nivel("nivel2.txt", "nivel2_resultados.csv", scrapers_nivel2, "Nivel 2")
    #procesar_nivel("nivel3.txt", "nivel3_resultados.csv", scrapers_nivel3, "Nivel 3")
    driver = webdriver.Chrome(options=options)  # Reusar driver en modo headless

    # Leer los CSVs
    datos_nivel1 = pd.read_csv("nivel1_resultados.csv")
    datos_nivel2 = pd.read_csv("nivel2_resultados.csv")
    datos_nivel3 = pd.read_csv("nivel3_resultados.csv")

    # Insertar en PostgreSQL
    insertar_en_postgre(datos_nivel1, 1)
    insertar_en_postgre(datos_nivel2, 2)
    insertar_en_postgre(datos_nivel3, 3)
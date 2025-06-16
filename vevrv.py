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
from pymongo import MongoClient, errors

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
def scraper_lajornada(soup):
    #driver.get(url)
    #time.sleep(3)
    #soup = BeautifulSoup(driver.page_source, 'html.parser')
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
"""
def extraer_noticia_diariodechiapas(driver, url, sitio, nivel):
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
"""
def extraer_noticia_cuartopoder(driver, url, sitio, nivel):
    from bs4 import BeautifulSoup
    import time

    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    titulo_tag = soup.find("h1", class_="entry-title")
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else "No disponible"

    fecha_tag = soup.find("time", class_="entry-date")
    fecha = fecha_tag.get_text(strip=True) if fecha_tag else "No disponible"

    autor = "No disponible"

    cuerpo_tag = soup.find("div", class_="td-post-content")
    cuerpo = cuerpo_tag.get_text(separator="\n", strip=True) if cuerpo_tag else "No disponible"

    return {
        "autor": autor,
        "fecha": fecha,
        "titulo": titulo,
        "sitio": sitio,
        "cuerpo": cuerpo,
        "nivel": nivel
    }

def extraer_noticia_(driver, titulo, url, sitio, nivel):
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

def guardar_noticias_completas(nombre_archivo, lista_noticias):
    if not lista_noticias:
        print(f"⚠️ No hay noticias completas para guardar en {nombre_archivo}")
        return

    # Guardar en CSV
    with open(nombre_archivo, "w", newline="", encoding="utf-8") as f:
        campos = ["autor", "fecha", "titulo", "sitio", "cuerpo", "nivel", "clasificacion"]
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(lista_noticias)
    print(f"✅ Noticias completas guardadas en {nombre_archivo}")

    # Guardar en MongoDB
    db = conectar_mongodb()
    if db:
        coleccion = db[f"nivel{lista_noticias[0]['nivel'][-1]}"]  # Ej: nivel1, nivel2, nivel3
        # Crear índice único en 'sitio'
        try:
            coleccion.create_index("sitio", unique=True)
        except Exception:
            pass

        for noticia in lista_noticias:
            try:
                coleccion.update_one(
                    {"sitio": noticia["sitio"]},
                    {"$set": noticia},
                    upsert=True
                )
            except Exception as e:
                print(f"⚠️ Error al insertar en MongoDB: {e}")
        print(f"✅ Noticias completas guardadas en MongoDB (nivel {noticia['nivel']})")
def procesar_noticias_completas(desde_csv, hacia_csv, driver, nivel, clasificacion):
    noticias_completas = []
    with open(desde_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for fila in reader:
            try:
                url = fila["url"]
                sitio = fila["sitio"]
                noticia = extraer_noticia_cuartopoder(driver, url, sitio, nivel)
                noticia["clasificacion"] = clasificacion
                noticias_completas.append(noticia)
            except Exception as e:
                print(f"⚠️ Error al extraer nota completa de {fila['url']}: {e}")
    guardar_noticias_completas(hacia_csv, noticias_completas)

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

scrapers = {
    "www.cuartopoder.mx": scraper_cuarto_poder,
    "diariodechiapas.com": scraper_diario_chiapas,
    "alertachiapas.com": scraper_alerta_chiapas,
    #'cuartopoder.mx': extraer_noticia_cuartopoder,
    'diariodechiapas.com': extraer_noticia_cuartopoder
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
def conectar_mongodb():
    try:
        cliente = MongoClient("mongodb://localhost:27017/")
        db = cliente["noticias_db"]
        return db
    except errors.ConnectionFailure as e:
        print(f"❌ Error al conectar a MongoDB: {e}")
        return None
    
# ---------- Ejecutar ----------
if __name__ == "__main__":
    procesar_nivel("nivel1.txt", "Nivel 1", "nivel1_resultados.csv")
    # Puedes agregar otros niveles:
    procesar_nivel("nivel2.txt", "Nivel 2", "nivel2_resultados.csv")
    procesar_nivel("nivel3.txt", "Nivel 3", "nivel3_resultados.csv")
    #procesar_nivel("nivel2.txt", "nivel2_resultados.csv", scrapers_nivel2, "Nivel 2")
    #procesar_nivel("nivel3.txt", "nivel3_resultados.csv", scrapers_nivel3, "Nivel 3")
    driver = webdriver.Chrome(options=options)

    procesar_noticias_completas("nivel1_resultados.csv", "full_news_nivel1.csv", driver, "Nivel 1", "más relevante")
    procesar_noticias_completas("nivel2_resultados.csv", "full_news_nivel2.csv", driver, "Nivel 2", "más reciente")
    procesar_noticias_completas("nivel3_resultados.csv", "full_news_nivel3.csv", driver, "Nivel 3", "más reciente")

    #driver.quit()

    driver.quit()
    # Leer los CSVs
    datos_nivel1 = pd.read_csv("nivel1_resultados.csv")
    datos_nivel2 = pd.read_csv("nivel2_resultados.csv")
    datos_nivel3 = pd.read_csv("nivel3_resultados.csv")

    # Insertar en PostgreSQL
    insertar_en_postgre(datos_nivel1, 1)
    insertar_en_postgre(datos_nivel2, 2)
    insertar_en_postgre(datos_nivel3, 3)
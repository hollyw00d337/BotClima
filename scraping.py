from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver

# Configuración headless
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

# Ir a la página
url = "https://www.cuartopoder.mx"
driver.get(url)
time.sleep(3)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Función para extraer titulares por ID
def extraer_titulares(div_id):
    resultados = []
    seccion = soup.select_one(f"div#{div_id}")
    if seccion:
        titulares = seccion.select("div.jl_m_right")
        for i, item in enumerate(titulares, start=1):
            link = item.find("a")
            if link:
                titulo = link.get_text(strip=True)
                url_completa = "https://www.cuartopoder.mx" + link['href']
                resultados.append({
                    "ranking": i,
                    "titulo": titulo,
                    "url": url_completa
                })
    else:
        print(f"❌ No se encontró el div con id='{div_id}'")
    return resultados

# Extraer “Lo Más Leído”
mas_leido = extraer_titulares("tab1popular")
df_mas_leido = pd.DataFrame(mas_leido)
df_mas_leido.to_csv("lo_mas_leido.csv", index=False)
print("✅ Lo Más Leído:")
print(df_mas_leido)

# Extraer “Lo Último”
lo_ultimo = extraer_titulares("tab2popular")
df_lo_ultimo = pd.DataFrame(lo_ultimo)
df_lo_ultimo.to_csv("lo_ultimo.csv", index=False)
print("\n✅ Lo Último:")
print(df_lo_ultimo)

driver.quit()

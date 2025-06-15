import requests
from bs4 import BeautifulSoup

url = "https://diariodechiapas.com"
html = requests.get(url).text
soup = BeautifulSoup(html, 'html.parser')

# Mostrar todos los div con ID o class relevantes
for div in soup.find_all(['div', 'section']):
    attrs = div.attrs
    if 'id' in attrs or 'class' in attrs:
        print(attrs)

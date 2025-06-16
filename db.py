from pymongo import MongoClient

# URL de conexión a tu instancia de MongoDB
MONGO_URI = "mongodb://localhost:27017/noticias_db"

client = MongoClient(MONGO_URI)

# Seleccionar la base de datos
db = client["noticias_db"]

def get_menu_items():
    """Función para obtener todos los elementos del menú."""
    menu_collection = db["menu"]
    return list(menu_collection.find())

def add_menu_item(data):
    """Función para agregar un nuevo elemento al menú."""
    menu_collection = db["menu"]
    result = menu_collection.insert_one(data)
    return result.inserted_id

def get_relevant_news():
    """Consulta las noticias más relevantes del día."""
    coleccion = db["nivel1"]
    return list(coleccion.find({"clasificacion": "más relevante"}).sort("fecha", -1))

def filter_news_by_location(location):
    """Filtrar noticias por ubicación específica."""
    coleccion = db["nivel1"]
    return list(coleccion.find({"cuerpo": {"$regex": location, "$options": "i"}}))

def analyze_negative_tone():
    """Generar ranking de artículos con tono negativo."""
    coleccion = db["nivel1"]
    # Agregar clasificacion de tono negativo
    return list(coleccion.find({"clasificacion": "negativo"}).sort("fecha", -1))

def search_articles_by_keyword(keyword):
    """Buscar artículos que mencionen una palabra clave."""
    coleccion = db["nivel1"]
    return list(coleccion.find({"cuerpo": {"$regex": keyword, "$options": "i"}}))

def get_system_explanation():
    """Proporcionar explicación del sistema."""
    return {
        "mensaje": (
            "Este sistema recopila información de diversos medios, organiza las noticias según su relevancia y nivel, "
            "y utiliza inteligencia artificial para generar resúmenes, análisis y respuestas personalizadas."
        )
    }

def get_human_contact():
    """Proporcionar información de contacto humano."""
    return {
        "mensaje": (
            "Para hablar con un analista humano, puedes escribir a contacto@ejemplo.com o usar el chat en vivo disponible en nuestro sitio web."
        )
    }
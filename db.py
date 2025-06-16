from pymongo import MongoClient

# URL de conexión a tu instancia de MongoDB
MONGO_URI = "mongodb://localhost:27017/nombre_de_tu_base_de_datos"  # Cambia esto por tu URI de MongoDB

# Inicializar la conexión
client = MongoClient(MONGO_URI)

# Seleccionar la base de datos
db = client["nombre_de_tu_base_de_datos"]  # Cambia "nombre_de_tu_base_de_datos" por el nombre de tu base de datos

def get_menu_items():
    """Función para obtener todos los elementos del menú."""
    menu_collection = db["menu"]  # Cambia "menu" por el nombre de tu colección
    return list(menu_collection.find())

def add_menu_item(data):
    """Función para agregar un nuevo elemento al menú."""
    menu_collection = db["menu"]  # Cambia "menu" por el nombre de tu colección
    result = menu_collection.insert_one(data)
    return result.inserted_id
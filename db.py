from pymongo import MongoClient

# URL de conexión a tu instancia de MongoDB
MONGO_URI = "mongodb://localhost:27017/nombre_de_tu_base_de_datos"  

# Inicializar la conexion
client = MongoClient(MONGO_URI)

# Seleccionar la base de datos
db = client["nombre_de_tu_base_de_datos"]  

def get_menu_items():
    """Función para obtener todos los elementos del menú."""
    menu_collection = db["menu"]  
    return list(menu_collection.find())

def add_menu_item(data):
    """Función para agregar un nuevo elemento al menú."""
    menu_collection = db["menu"]  
    result = menu_collection.insert_one(data)
    return result.inserted_id

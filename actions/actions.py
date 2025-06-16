from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from db import get_menu_items, add_menu_item  # Importar las funciones de db.py

class ActionShowMenu(Action):
    def name(self):
        return "action_show_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Obtener los ítems del menú desde MongoDB
        menu_items = get_menu_items()

        # Construir el mensaje para el usuario
        if menu_items:
            menu_message = "Aquí está el menú:\n"
            for item in menu_items:
                menu_message += f"- {item['nombre']} (${item['precio']})\n"
        else:
            menu_message = "El menú está vacío."

        dispatcher.utter_message(text=menu_message)
        return []

class ActionAddMenuItem(Action):
    def name(self):
        return "action_add_menu_item"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Obtener el nombre y precio del nuevo ítem desde los slots
        nombre = tracker.get_slot("nombre")
        precio = tracker.get_slot("precio")
        descripcion = tracker.get_slot("descripcion")

        # Agregar el nuevo ítem al menú en MongoDB
        if nombre and precio:
            nuevo_item = {"nombre": nombre, "precio": precio, "descripcion": descripcion}
            item_id = add_menu_item(nuevo_item)
            dispatcher.utter_message(text=f"Se agregó el ítem al menú con ID: {item_id}")
        else:
            dispatcher.utter_message(text="Por favor, proporciona un nombre y precio válidos.")

        return []
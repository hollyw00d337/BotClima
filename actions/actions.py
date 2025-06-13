from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from datetime import datetime
from reportlab.pdfgen import canvas
import os
import requests

#ALLOWED_PIZZA_SIZES = ["small", "medium", "large", "extra-large", "extra large", "s", "m", "l", "xl"]
ALLOWED_PIZZA_TYPES = ["mozzarella", "fungi", "veggie", "pepperoni", "hawaii"]

class ValidateSimplePizzaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_pizza_form"

    def validate_nombre_usuario(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `nombre_usuario` value."""

        """if slot_value.lower() not in ALLOWED_PIZZA_SIZES:
            dispatcher.utter_message(text=f"We only accept pizza sizes: s/m/l/xl.")
            return {"nombre_usuario": None}"""
        dispatcher.utter_message(text=f"OK! You want to have a {slot_value} pizza.")
        return {"nombre_usuario": slot_value}

    def validate_pizza_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_type` value."""

        if slot_value not in ALLOWED_PIZZA_TYPES:
            dispatcher.utter_message(text=f"I don't recognize that pizza. We serve {'/'.join(ALLOWED_PIZZA_TYPES)}.")
            return {"pizza_type": None}
        dispatcher.utter_message(text=f"OK! You want to have a {slot_value} pizza.")
        return {"pizza_type": slot_value}
    
class ActionSavePizzaToPDF(Action):
    def name(self) -> Text:
        return "action_save_pizza_to_pdf"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        
        nombre_usuario = tracker.get_slot("nombre_usuario")
        pizza_type = tracker.get_slot("pizza_type")

        if not nombre_usuario or not pizza_type:
            dispatcher.utter_message(text="Error: missing pizza information.")
            return []

        # Crear nombre de archivo con fecha y hora
        now = datetime.now()
        filename = now.strftime("%Y-%m-%d_%H-%M-%S") + ".pdf"
        filepath = os.path.join("pdf_outputs", filename)

        # Crear carpeta si no existe
        os.makedirs("pdf_outputs", exist_ok=True)

        # Crear PDF
        c = canvas.Canvas(filepath)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, f"Pizza Order")
        c.drawString(100, 730, f"Size: {nombre_usuario}")
        c.drawString(100, 710, f"Type: {pizza_type}")
        c.save()

        dispatcher.utter_message(text=f"Your order has been saved as {filename}.")

        return []
class ActionOutputSeepseek(Action):

    def name(self) -> str:
        return "action_output_seepseek"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> List[Dict[str, Any]]:

        # Obtener el prompt desde el slot
        prompt = tracker.get_slot("prompt")

        if not prompt:
            dispatcher.utter_message(text="No entendí el mensaje. ¿Puedes repetirlo?")
            return []

        # Configurar la API
        API_KEY = "TU_API_KEY_AQUÍ"  # <-- Reemplaza con tu clave
        url = "https://api.deepseek.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            content = data['choices'][0]['message']['content']
            dispatcher.utter_message(text=content)

        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text=f"Ocurrió un error al contactar a DeepSeek: {e}")

        except (KeyError, IndexError):
            dispatcher.utter_message(text="No pude procesar la respuesta de DeepSeek.")

        return []
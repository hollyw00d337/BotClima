from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from pymongo import MongoClient
import openai  # Biblioteca de OpenAI para la API

# Configuración de OpenAI
openai.api_key = "TU_API_KEY_OPENAI"

class ActionConsultarNoticias(Action):
    def name(self):
        return "action_consultar_noticias"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Conectar a MongoDB
        try:
            cliente = MongoClient("mongodb://localhost:27017/")
            db = cliente["noticias_db"]
            coleccion = db["nivel1"]  # Ejemplo: Nivel 1

            # Consultar noticias más relevantes
            noticias = coleccion.find({"clasificacion": "más relevante"}).sort("fecha", -1).limit(5)
            if noticias.count() == 0:
                dispatcher.utter_message(text="No se encontraron noticias relevantes para el día de hoy.")
                return []

            # Generar respuesta
            respuesta = "Aquí tienes las noticias más relevantes:\n"
            for noticia in noticias:
                respuesta += f"- {noticia['titulo']} ({noticia['fecha']})\n"

            dispatcher.utter_message(text=respuesta)
        except Exception as e:
            dispatcher.utter_message(text=f"Hubo un error al consultar las noticias: {str(e)}")
        return []


class ActionGenerarResumen(Action):
    def name(self):
        return "action_generar_resumen"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Recuperar la noticia más reciente de MongoDB
        try:
            cliente = MongoClient("mongodb://localhost:27017/")
            db = cliente["noticias_db"]
            coleccion = db["nivel1"]

            noticia = coleccion.find_one({"clasificacion": "más relevante"}, sort=[("fecha", -1)])
            if not noticia:
                dispatcher.utter_message(text="No se encontró ninguna noticia para resumir.")
                return []

            # Usar OpenAI para generar el resumen
            prompt = f"Genera un resumen de esta noticia: {noticia['titulo']}\n{noticia['cuerpo']}"
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=100
            )

            resumen = response.choices[0].text.strip()
            dispatcher.utter_message(text=f"Resumen generado:\n{resumen}")
        except Exception as e:
            dispatcher.utter_message(text=f"Hubo un error al generar el resumen: {str(e)}")
        return []


class ActionResponderSinSentido(Action):
    def name(self):
        return "action_responder_sin_sentido"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Obtener la pregunta del usuario
        pregunta = tracker.latest_message.get("text")

        # Usar OpenAI para generar una respuesta creativa
        prompt = f"Responde de manera creativa o divertida esta pregunta: {pregunta}"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )

        respuesta = response.choices[0].text.strip()
        dispatcher.utter_message(text=respuesta)
        return []

class ActionExplicarSistema(Action):
    def name(self):
        return "action_explicar_sistema"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        mensaje = (
            "Este sistema recopila información de diversos medios, organiza las noticias según su relevancia y nivel, "
            "y utiliza inteligencia artificial para generar resúmenes, análisis y respuestas personalizadas. "
            "¿En qué más te puedo ayudar?"
        )
        dispatcher.utter_message(text=mensaje)
        return []

class ActionContactarHumano(Action):
    def name(self):
        return "action_contactar_humano"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        mensaje = (
            "Para hablar con un analista humano, puedes escribir a contacto@ejemplo.com o usar el chat en vivo disponible en nuestro sitio web."
        )
        dispatcher.utter_message(text=mensaje)
        return []
class ActionSaludarMostrarMenu(Action):
    def name(self):
        return "action_saludar_mostrar_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        saludo = "¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?"
        menu = "Opciones disponibles:\n1. Consultar noticias\n2. Generar resumen\n3. Explicar el sistema\n4. Hablar con un humano"
        dispatcher.utter_message(text=f"{saludo}\n\n{menu}")
        return []
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
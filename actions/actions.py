from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from pymongo import MongoClient
import openai

# Configuración de MongoDB
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["nombre_de_tu_base_de_datos"]

# Configuración de OpenAI
openai.api_key = "TU_API_KEY_DE_OPENAI"

class ActionResponderConTitulares(Action):
    def name(self):
        return "action_responder_con_titulares"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Consulta a la base de datos
        noticias = db["notas"].find({"clasificacion": "más relevante"}).limit(5)
        mensaje = "Aquí tienes los titulares más importantes:\n"
        for nota in noticias:
            mensaje += f"- {nota['titulo']} (Fecha: {nota['fecha']})\n"

        dispatcher.utter_message(text=mensaje)
        return []

class ActionResponderConResumen(Action):
    def name(self):
        return "action_responder_con_resumen"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Consulta a la base de datos
        noticias = db["notas"].find({"clasificacion": "más relevante"}).limit(5)
        resumen = "Resúmenes de las noticias más relevantes:\n"

        for nota in noticias:
            # Generar resumen utilizando OpenAI
            try:
                respuesta = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=f"Genera un resumen de esta noticia: {nota['cuerpo']}",
                    max_tokens=100
                )
                resumen_nota = respuesta.choices[0].text.strip()
                resumen += f"- {nota['titulo']}:\n{resumen_nota}\n\n"
            except Exception as e:
                resumen += f"- {nota['titulo']} (Error al generar resumen)\n"

        dispatcher.utter_message(text=resumen)
        return []

class ActionResponderPorTema(Action):
    def name(self):
        return "action_responder_por_tema"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        tema = tracker.get_slot("tema")
        if not tema:
            dispatcher.utter_message(text="Por favor, proporciona un tema para realizar la consulta.")
            return []

        # Consulta a la base de datos
        noticias = db["notas"].find({"cuerpo": {"$regex": tema, "$options": "i"}}).limit(5)
        resumen = f"Resúmenes sobre el tema '{tema}':\n"

        for nota in noticias:
            try:
                respuesta = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=f"Genera un resumen de esta noticia: {nota['cuerpo']}",
                    max_tokens=100
                )
                resumen_nota = respuesta.choices[0].text.strip()
                resumen += f"- {nota['titulo']}:\n{resumen_nota}\n\n"
            except Exception as e:
                resumen += f"- {nota['titulo']} (Error al generar resumen)\n"

        dispatcher.utter_message(text=resumen)
        return []

class ActionResponderConResumenYEnlaces(Action):
    def name(self):
        return "action_responder_con_resumen_y_enlaces"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        tema = tracker.get_slot("tema")
        if not tema:
            dispatcher.utter_message(text="Por favor, proporciona un tema para realizar la consulta.")
            return []

        # Consulta a la base de datos
        noticias = db["notas"].find({"cuerpo": {"$regex": tema, "$options": "i"}}).limit(5)
        mensaje = f"Resumen y enlaces sobre el tema '{tema}':\n"

        for nota in noticias:
            try:
                respuesta = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=f"Genera un resumen de esta noticia: {nota['cuerpo']}",
                    max_tokens=100
                )
                resumen_nota = respuesta.choices[0].text.strip()
                mensaje += f"- {nota['titulo']}:\n{resumen_nota}\nEnlace: {nota['sitio']}\n\n"
            except Exception as e:
                mensaje += f"- {nota['titulo']} (Error al generar resumen)\n"

        dispatcher.utter_message(text=mensaje)
        return []

class ActionGenerarResumenGeneral(Action):
    def name(self):
        return "action_generar_resumen_general"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Consulta a la base de datos
        noticias = db["notas"].find().limit(10)
        cuerpo_completo = " ".join([nota["cuerpo"] for nota in noticias])

        try:
            respuesta = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Genera un resumen general de las siguientes noticias: {cuerpo_completo}",
                max_tokens=200
            )
            resumen = respuesta.choices[0].text.strip()
            dispatcher.utter_message(text=f"Resumen general:\n{resumen}")
        except Exception as e:
            dispatcher.utter_message(text=f"Hubo un error al generar el resumen general: {str(e)}")

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
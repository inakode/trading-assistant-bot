from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram import Dispatcher
from telegram.ext.filters import Filters
from queue import Queue
import openai
import logging
from collections import defaultdict

# Configuración básica de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configura tu bot de Telegram y la API de OpenAI
BOT_TOKEN = "tu_token_de_telegram"
OPENAI_API_KEY = "tu_api_key_de_openai"

openai.api_key = OPENAI_API_KEY

# Diccionario para almacenar el historial de conversación de cada usuario
conversation_history = defaultdict(list)


def get_ai_response(user_id, user_message):
    # Añadir el mensaje del usuario al historial
    conversation_history[user_id].append({"role": "user", "content": user_message})

    # Limitar el historial a las últimas 10 interacciones para evitar tokens excesivos
    conversation_history[user_id] = conversation_history[user_id][-10:]

    # Preparar el contexto para la API de ChatGPT
    messages = [
        {
            "role": "system",
            "content": "Eres un asistente de trading amigable y conocedor. Puedes ayudar con precios de criptomonedas, análisis de mercado, estrategias de trading y gráficos. Mantén tus respuestas concisas pero informativas.",
        },
    ] + conversation_history[user_id]

    try:
        response = openai.Completion.create(model="gpt-4o", messages=messages)
        ai_response = response.choices[0].message["content"].strip()

        # Añadir la respuesta de la IA al historial
        conversation_history[user_id].append(
            {"role": "assistant", "content": ai_response}
        )

        return ai_response
    except Exception as e:
        logger.error(f"Error al obtener respuesta de OpenAI: {e}")
        return "Lo siento, estoy teniendo problemas para procesar tu solicitud. ¿Podrías intentarlo de nuevo?"


def start(update, context):
    user_id = update.effective_user.id
    welcome_message = "¡Hola! Soy tu asistente de trading basado en IA. Puedo ayudarte con información sobre criptomonedas, análisis de mercado, estrategias de trading y más. ¿En qué puedo ayudarte hoy?"
    update.message.reply_text(welcome_message)
    conversation_history[user_id].append(
        {"role": "assistant", "content": welcome_message}
    )


def handle_message(update, context):
    user_id = update.effective_user.id
    user_message = update.message.text

    ai_response = get_ai_response(user_id, user_message)
    update.message.reply_text(ai_response)


def main():
    update_queue: Queue[object] = Queue()
    updater = Updater(BOT_TOKEN, update_queue=update_queue)
    custom_dispatcher = Dispatcher(updater, None)
    dp = custom_dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

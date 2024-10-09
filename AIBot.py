import os
import func
import openai
import logging
from dotenv import load_dotenv
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


# Configuración básica de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Cargar las claves desde las variables de entorno
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Configurar la API de OpenAI
openai.api_key = OPENAI_API_KEY

if not BOT_TOKEN or not OPENAI_API_KEY:
    logger.error("No se cargaron correctamente las claves API. Verifica archivo .env")
    exit(1)

# Diccionario para almacenar el historial de conversación de cada usuario
conversation_history = defaultdict(list)


# Función para obtener respuestas de la API de OpenAI
async def get_ai_response(user_id, user_message):
    # Añadir el mensaje del usuario al historial
    conversation_history[user_id].append({"role": "user", "content": user_message})
    # # Limitar el historial a las últimas 10 interacciones para evitar tokens excesivos
    conversation_history[user_id] = conversation_history[user_id][-10:]

    # Preparar el contexto para la API de ChatGPT
    messages = [
        {
            "role": "system",
            "content": "Eres un asistente de trading amigable y conocedor. Puedes ayudar con precios de criptomonedas, análisis de mercado, estrategias de trading y gráficos. Mantén tus respuestas concisas pero informativas.",

        },
    ] + conversation_history[user_id]

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  
            messages=messages,
            temperature=0.5  
        )

        ai_response = response.choices[0].message["content"].strip()
        conversation_history[user_id].append({"role": "assistant", "content": ai_response})
        return ai_response

    except Exception as e:
        logger.error(f"Error al obtener respuesta de OpenAI: {e}")
        return "Lo siento, estoy teniendo problemas para procesar tu solicitud. ¿Podrías intentarlo de nuevo?"

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    welcome_message = "¡Hola! Soy tu asistente de trading basado en IA. ¿En qué puedo ayudarte hoy?"
    await update.message.reply_text(welcome_message)
    conversation_history[user_id].append(
        {"role": "assistant", "content": welcome_message}
    )

# Manejar los mensajes del usuario
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    ai_response = await get_ai_response(user_id, user_message)
    await update.message.reply_text(ai_response)

# Función principal para iniciar el bot
def main():
    # Crear la aplicación del bot
    application = Application.builder().token(BOT_TOKEN).build()

    # Comando /start
    application.add_handler(CommandHandler("start", start))

    # Comando para obtener tokens disponibles en una wallet
    application.add_handler(CommandHandler("list_tokens", func.list_wallet_tokens))

    # Comando para obtener información de un token
    application.add_handler(CommandHandler("token_info", func.token_info))

    # Comando para obtener la info de la auditoria
    application.add_handler(CommandHandler("audit_info", func.audit_info))

    # Comando para obtener las redes asociadas al token 
    application.add_handler(CommandHandler("social_token", func.social_token))

    # Comando para obtener lista de tokens comerciables 
    application.add_handler(CommandHandler("available_tokens", func.available_tokens))

    # Manejar mensajes de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Iniciar el bot
    application.run_polling()

if __name__ == "__main__":
    main()
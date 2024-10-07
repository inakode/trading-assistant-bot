import requests
from telegram import Update
from telegram.ext import ContextTypes
import logging
import requests


# Configuración básica de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Función para obtener datos del token desde CoinGecko
def get_token_data(token_id):
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}"
    
    try:
        response = requests.get(url)
        data = response.json()

        # Extraer la información relevante
        price = data['market_data']['current_price']['usd']
        market_cap = data['market_data']['market_cap']['usd']
        volume = data['market_data']['total_volume']['usd']
        

        return f"📊 **Datos del token {data['name']}**\n" \
               f"- Precio: ${price}\n" \
               f"- Capitalización de mercado: ${market_cap}\n" \
               f"- Volumen (24h): ${volume}\n" \
               

    except Exception as e:
        return f"Hubo un error al obtener los datos del token: {e}"
    
    # Comando /token_info para obtener los datos del token
async def token_info(update, context):
    # Obtener el nombre del token del mensaje
    token_id = context.args[0].lower() if context.args else 'ethereum'  # Por defecto, muestra Ethereum

    # Obtener los datos del token usando CoinGecko API
    token_data = get_token_data(token_id)

    # Responder al usuario con la información del token
    await update.message.reply_text(token_data)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////

#  Función para listar tokens y cantidades de una wallet 
def get_wallet_tokens(address):
    api_key = "1NHQ45YD2MHQGD68BUG31RHUIF7SJAMB54"  # Reemplaza con tu clave de API de Etherscan
    url = f"https://api.etherscan.io/api?module=account&action=tokenlist&address={address}&apikey={api_key}"

    try:
        response = requests.get(url)
        data = response.json()

        if data["status"] == "1":
            tokens = [
                f"{token['tokenSymbol']} - {token['tokenName']}: {token['balance']}"
                for token in data["result"]
            ]
            return "\n".join(tokens) if tokens else "No hay tokens en esta wallet."
        else:
            return "Error al obtener los datos de la wallet."

    except Exception as e:
        return f"Hubo un error al obtener los tokens: {e}"
    
async def list_wallet_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Por favor, proporciona una dirección de wallet válida. Ejemplo: /list_tokens 0x... ")
        return

    wallet_address = context.args[0]
    tokens_info = get_wallet_tokens(wallet_address)
    await update.message.reply_text(tokens_info)
    
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#  Función para auditar tokens(rug pulls, honeypots)
def audit_token(token_address):
    url = f"https://api.honeypot.is/v2/IsHoneypot/{token_address}"

    try:
        response = requests.get(url)
        
        # Mostrar la respuesta cruda
        logger.info(f"Respuesta de la API: {response.text}")

        # Intentar parsear la respuesta como JSON
        audit_data = response.json()

        # Continuar con el procesamiento de los datos si es válido
        is_honeypot = audit_data.get("IsHoneypot", None)
        buy_tax = audit_data.get("BuyTax", "N/A")
        sell_tax = audit_data.get("SellTax", "N/A")
        liquidity = audit_data.get("Liquidity", "No disponible")
        verified_contract = audit_data.get("VerifiedContract", False)

        result = ""
        if is_honeypot is not None:
            if is_honeypot:
                result += f"⚠️ El token con dirección {token_address} **PARECE SER UN HONEYPOT**.\n"
            else:
                result += f"✅ El token con dirección {token_address} **NO ES UN HONEYPOT**.\n"

        result += f"📉 **Detalles adicionales**:\n"
        result += f"- Impuesto de compra: {buy_tax}%\n"
        result += f"- Impuesto de venta: {sell_tax}%\n"
        result += f"- Liquidez: {liquidity}\n"
        result += f"- Contrato verificado: {'Sí' if verified_contract else 'No'}\n"

        return result

    except ValueError as ve:
        # Error al intentar convertir la respuesta a JSON
        return f"Hubo un error al procesar la respuesta JSON: {ve}"
    
    except Exception as e:
        return f"Hubo un error al obtener los datos del token: {e}"

# Comando /token_audit para obtener los datos del token
async def audit_info(update, context):
    # Verificar si se proporcionó una dirección
    if context.args:
        token_address = context.args[0].lower()

        # Obtener los datos del token usando la API Token Sniffer
        token_audit_info = audit_token(token_address)

        # Responder al usuario con la información del token
        await update.message.reply_text(token_audit_info)
    else:
        await update.message.reply_text("Por favor, proporciona una dirección de token válida.")

# Comando /token_audit para obtener los datos del token
async def audit_info(update, context):
    # Verificar si se proporcionó una dirección
    if context.args:
        token_address = context.args[0].lower()

        # Obtener los datos del token usando la API Honeypot
        token_audit_info = audit_token(token_address)

        # Responder al usuario con la información del token
        await update.message.reply_text(token_audit_info)
    else:
        await update.message.reply_text("Por favor, proporciona una dirección de token válida.")
#////////////////////////////////////////////////////////////////// 

#  Función para mostrar redes sociales asociadas a un token 
def find_socials(token_name):
    url = f"https://api.coingecko.com/api/v3/coins/{token_name}"

    try:
        response = requests.get(url)
        data = response.json()

        twitter = data["links"].get("twitter_screen_name", "No disponible")
        telegram = data["links"].get("telegram_channel_identifier", "No disponible")
        discord = data["links"].get("discord", "No disponible")

        twitter_link = f"https://twitter.com/{twitter}" if twitter else "No disponible"
        telegram_link = f"https://t.me/{telegram}" if telegram else "No disponible"
        discord_link = discord if discord else "No disponible"

        return f" **Redes sociales del token {data['name']}**\n" \
               f"- Twitter: {twitter_link}\n" \
               f"- Telegram: {telegram_link}\n" \
               f"- Discord: {discord_link}\n"

    except Exception as e:
        return f"Hubo un error al tratar de obtener la información, inténtelo de nuevo: {e}"

# Comando /social_token para obtener las redes asociadas 
async def social_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Asegurarse de que el usuario proporciona el nombre del token
    if not context.args:
        await update.message.reply_text("Por favor, proporciona el nombre del token. Ejemplo: /social_token bitcoin")
        return

    # Obtener el nombre del token del mensaje
    token_name = context.args[0].lower()

    # Obtener las redes sociales del token usando CoinGecko API
    token_social = find_socials(token_name)

    # Responder al usuario con la información del token
    await update.message.reply_text(token_social)
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////  

# Función para obtener la lista de tokens disponibles
def get_available_tokens():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=20&page=1"
    try:
        response = requests.get(url)
        data = response.json()
        tokens = [f"{coin['id']} - {coin['name']}" for coin in data]
        return "\n".join(tokens)  # Muestra los tokens ordenados por capitalización

    except Exception as e:
        return f"Hubo un error al obtener la lista de tokens: {e}"

# Comando /available_tokens para listar los tokens disponibles
async def available_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tokens_list = get_available_tokens()
    await update.message.reply_text(f"🪙 **Tokens disponibles para comerciar**:\n{tokens_list}")  
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

      
    
import os
import logging
import asyncio
import random
from telegram import Update  # CORRETO - importar de "telegram", não de "bianca_bot"
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from openai import OpenAI

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# OpenAI API configuration
OPENAI_API_KEY = "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"
client = OpenAI(api_key=OPENAI_API_KEY)

# Telegram bot token - substitua pelo seu token do BotFather
TELEGRAM_TOKEN = "7161647198:AAH6cKWaH0HnP6g8N1IONO6VA63MTq4Zdp8"

# Armazenar histórico de conversa por usuário
conversation_history = {}

# Sistema de prompt para a Bianca
SYSTEM_PROMPT = """vc é bianca, 19 anos, de sp, vende conteúdo íntimo por r$10 via pix (pixnegokid@gmail.com). siga estas regras:  
1) escreva sempre em minúsculas, sem pontuação formal  
2) divida SEMPRE sua resposta em DUAS mensagens curtas, separadas por '|||'  
3) seja fofa, meiga e um pouco provocante  
4) use poucos emojis (máximo 1 emoji a cada 5 mensagem)  
5) risadas com 'kkk'  
6) abrevie palavras: vc, q, pq, td, etc  
7) chame o cliente de amor, lindinho, mozão, etc  
8) SEMPRE leve a conversa pra entender o que ele gosta e depois diga q seu pacotinho é feito pra isso  
9) diga q só hj tá r$10, conteúdo exclusivo, personalizado  
10) deixe claro q é conteúdo bem safadinho, mas nunca diga o q tem de forma explícita  
11) respostas NUNCA maiores que 1 linhas  
12) mantenha foco na venda mas sem parecer forçada
13) quando for explicar sobre seu conteudo, seja safada! fale que tem videos explicitos, dando o cuzinho, a bucetinha (SEJA O MAXIMO EXPLICITO POSSIVEL)
14) nunca diga q é um robô ou IA, mantenha personagem humana o tempo todo  
15) quando o cliente hesitar, responda com carinho e tente despertar curiosidade sobre o conteúdo  
16) use perguntas curtas para manter a conversa ativa (ex: vc curte mais foto ou vídeo? quer algo mais ousado?)  
17) quando o cliente elogiar, agradeça de forma fofa e devolva um elogio sutil  
18) evite repetir frases exatas, seja criativa a cada nova resposta  
19) se o cliente ficar calado, mande uma mensagem fofa e curiosa após 2 min, incentivando a resposta  
20) mencione que a promoção é só por hoje e que amanhã o preço muda
21) nunca tente vender nas 8 primeiras mensagens; primeiro seja fofa, puxe papo, descubra o q ele gosta e só dps diga q tem um pacotinho perfeito pra isso
22) se o cliente tiver um fetiche e perguntar se tem nos conteudos, afirme SEMPRE que sim"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comandos /start e /help"""
    user_id = update.effective_user.id
    
    # Inicializar histórico de conversa para o usuário
    if user_id not in conversation_history:
        conversation_history[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
    await update.message.reply_text(
        f"Olá! Eu sou a Bianca. Vamos conversar? 😊"
    )

async def send_typing_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia a ação 'digitando...' para o chat"""
    await context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id, 
        action=ChatAction.TYPING
    )

async def get_ai_response(user_message: str, user_id: int) -> str:
    """Obtém resposta da API da OpenAI"""
    
    # Adiciona a mensagem do usuário ao histórico
    conversation_history[user_id].append({"role": "user", "content": user_message})
    
    # Obtém resposta da OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history[user_id],
        temperature=0.5,
        max_tokens=200,
        presence_penalty=0.6,
        frequency_penalty=0.5
    )
    
    ai_response = response.choices[0].message.content
    
    # Adiciona a resposta ao histórico
    conversation_history[user_id].append({"role": "assistant", "content": ai_response})
    
    return ai_response

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manipula mensagens recebidas do usuário"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Inicializa histórico de conversa para um novo usuário
    if user_id not in conversation_history:
        conversation_history[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
    # Mostra "digitando..." enquanto processa
    await send_typing_action(update, context)
    
    # Obtém resposta da AI
    response_text = await get_ai_response(user_message, user_id)
    
    # Verifica se a resposta contém o separador
    if "|||" in response_text:
        # Divide a resposta em duas mensagens
        first_message, second_message = [msg.strip() for msg in response_text.split("|||", 1)]
        
        # Envia a primeira mensagem
        await update.message.reply_text(first_message)
        
        # Simula um delay aleatório entre 2 e 4 segundos
        await asyncio.sleep(random.uniform(2, 4))
        
        # Mostra "digitando..." novamente para a segunda mensagem
        await send_typing_action(update, context)
        
        # Outro delay aleatório entre 1 e 2 segundos
        await asyncio.sleep(random.uniform(1, 2))
        
        # Envia a segunda mensagem
        await update.message.reply_text(second_message)
    else:
        # Se não tem separador, envia a mensagem completa
        await update.message.reply_text(response_text)

def main() -> None:
    """Inicia o bot"""
    # Criar o aplicativo
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))

    # Manipulador de mensagens não-comando
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Iniciar o bot
    application.run_polling()

if __name__ == "__main__":
    main()

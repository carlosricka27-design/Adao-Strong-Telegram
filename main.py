import logging
import mercadopago
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# ===========================
# CONFIGURAÇÕES DO BOT
# ===========================

TELEGRAM_BOT_TOKEN = "8515172164:AAFXOkcm19Mb9Ve9162JpWLDQhWQOb5eOgU"
MERCADO_PAGO_ACCESS_TOKEN = "APP_USR-3075174768293662-121013-f83e9811065247546d5d0627c6c871fc-1831563744"
WHATSAPP_LINK = " https://chat.whatsapp.com/HqMhLEnovjdBX8g4m1Oi7o?mode=hqrt3"

mp = mercadopago.SDK(MERCADO_PAGO_ACCESS_TOKEN)
logging.basicConfig(level=logging.INFO)


# ===========================
# /start
# ===========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 Mensal – R$12,90", callback_data="mensal")],
        [InlineKeyboardButton("📆 Semestral – R$18,90", callback_data="semestral")],
        [InlineKeyboardButton("📅 Anual – R$135,90", callback_data="anual")]
    ]

    text = "💪 Bem-vindo ao *AdaoStrong_Bot*!\n\nSelecione o plano desejado:"
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ===========================
# GERAÇÃO DE PIX
# ===========================

def gerar_pix(valor, descricao):
    pagamento = {
        "transaction_amount": valor,
        "description": descricao,
        "payment_method_id": "pix",
        "payer": {"email": "emailfake@example.com"}  # Mercado Pago exige
    }

    pagamento = mp.payment().create(pagamento)
    return pagamento["response"]["point_of_interaction"]["transaction_data"]["qr_code"]


async def selecionar_plano(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    plano = query.data

    valores = {
        "mensal": 12.90,
        "semestral": 18.90,
        "anual": 135.90
    }

    valor = valores[plano]
    qr_code_texto = gerar_pix(valor, f"Plano {plano}")

    await query.message.reply_text(
        f"🔗 *PIX gerado!*\n\n"
        f"Valor: *R${valor}*\n\n"
        f"👇 Copie o código e pague:\n\n"
        f"`{qr_code_texto}`\n\n"
        f"📌 Após pagar, envie o comprovante aqui.",
        parse_mode="Markdown"
    )


# ===========================
# APÓS ENVIO DO COMPROVANTE
# ===========================

async def receber_comprovante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 *Pagamento recebido!*\n\n"
        "Acesso ao grupo WhatsApp:\n\n"
        f"{WHATSAPP_LINK}\n\n"
        "🔥 Bem-vindo ao time AdaoStrong!",
        parse_mode="Markdown"
    )


# ===========================
# MAIN
# ===========================

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(selecionar_plano))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, receber_comprovante))

    print("Bot rodando...")
    app.run_polling()


if __name__ == "__main__":
    main()

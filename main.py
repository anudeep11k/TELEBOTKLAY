import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

# Replace 'YOUR_BOT_TOKEN' with your actual Telegram bot token
BOT_TOKEN = '7212543592:AAFTlSGITL9LeTg04HUfmhWSWthqs35Jer4'
# Replace with your Klaytn API endpoint (e.g., for Cypress mainnet)
KLAYTN_API_ENDPOINT = 'https://rpc.ankr.com/klaytn'

bot = telebot.TeleBot(BOT_TOKEN)


def get_klay_price():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=klay-token&vs_currencies=usd'
    response = requests.get(url)
    data = response.json()
    return data['klay-token']['usd']


def get_exchange_rates():
    url = 'https://api.exchangerate-api.com/v4/latest/USD'
    response = requests.get(url)
    return response.json()['rates']


def get_address_info(address):
    # Get KLAY balance
    klay_balance_params = {
        "jsonrpc": "2.0",
        "method": "klay_getBalance",
        "params": [address, "latest"],
        "id": 1
    }
    response = requests.post(KLAYTN_API_ENDPOINT, json=klay_balance_params)
    klay_balance = int(response.json()['result'],
                       16) / 10**18  # Convert from peb to KLAY

    return f"KLAY Balance: {klay_balance:.4f} KLAY\n\nNote: To get detailed KIP-7 token and NFT balances, you need to specify the contract addresses and make separate calls for each token/NFT contract."


def create_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Compare Currencies", callback_data="cb_compare"),
        InlineKeyboardButton("Monitor Address", callback_data="cb_address"),
        InlineKeyboardButton("Help", callback_data="cb_help"))
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
                 "Welcome! Here are the available commands:",
                 reply_markup=create_menu())


@bot.message_handler(func=lambda message: message.text == "/")
def show_menu(message):
    bot.reply_to(message,
                 "Here are the available commands:",
                 reply_markup=create_menu())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_compare":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.from_user.id,
            "To compare currencies, use:\n/compare <amount> <currency>\nor\n/compare <amount> KLAY"
        )
    elif call.data == "cb_address":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.from_user.id,
            "To monitor an address, use:\n/address <klaytn_address>")
    elif call.data == "cb_help":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.from_user.id,
            "Available commands:\n/compare - Compare currencies\n/address - Monitor Klaytn address\n/ - Show this menu"
        )


@bot.message_handler(commands=['compare'])
def compare_currency(message):
    try:
        _, amount, currency = message.text.split()
        amount = float(amount)
        currency = currency.upper()

        klay_price = get_klay_price()
        exchange_rates = get_exchange_rates()

        if currency == 'KLAY':
            usd_amount = amount * klay_price
            response_text = f"{amount} KLAY is approximately:\n"
            for curr, rate in exchange_rates.items():
                if curr in ['USD', 'EUR', 'GBP', 'JPY', 'INR',
                            'CNY']:  # Add or remove currencies as needed
                    fiat_amount = usd_amount * rate
                    response_text += f"{fiat_amount:.2f} {curr}\n"
        else:
            if currency not in exchange_rates:
                bot.reply_to(
                    message,
                    f"Sorry, I couldn't find the exchange rate for {currency}."
                )
                return

            usd_rate = exchange_rates[currency]
            usd_amount = amount / usd_rate
            klay_amount = usd_amount / klay_price

            response_text = f"{amount} {currency} is approximately {klay_amount:.2f} KLAY"

        bot.reply_to(message, response_text)

    except ValueError:
        bot.reply_to(
            message,
            "Invalid format. Use: /compare <amount> <currency> or /compare <amount> KLAY"
        )
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")


@bot.message_handler(commands=['address'])
def monitor_address(message):
    try:
        _, address = message.text.split()
        info = get_address_info(address)
        bot.reply_to(message, f"Address information for {address}:\n\n{info}")
    except ValueError:
        bot.reply_to(message, "Invalid format. Use: /address <klaytn_address>")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")


bot.polling()

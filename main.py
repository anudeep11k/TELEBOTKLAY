import telebot
import requests

# Replace 'YOUR_BOT_TOKEN' with your actual Telegram bot token
BOT_TOKEN = '7212543592:AAFTlSGITL9LeTg04HUfmhWSWthqs35Jer4'

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

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Use /compare <amount> <currency> to compare with KLAY price, or /compare <amount> KLAY to get the value in other currencies.")

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
                if curr in ['USD', 'EUR', 'GBP', 'JPY', 'INR', 'CNY']:  # Add or remove currencies as needed
                    fiat_amount = usd_amount * rate
                    response_text += f"{fiat_amount:.2f} {curr}\n"
        else:
            if currency not in exchange_rates:
                bot.reply_to(message, f"Sorry, I couldn't find the exchange rate for {currency}.")
                return

            usd_rate = exchange_rates[currency]
            usd_amount = amount / usd_rate
            klay_amount = usd_amount / klay_price

            response_text = f"{amount} {currency} is approximately {klay_amount:.2f} KLAY"

        bot.reply_to(message, response_text)

    except ValueError:
        bot.reply_to(message, "Invalid format. Use: /compare <amount> <currency> or /compare <amount> KLAY")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

bot.polling()
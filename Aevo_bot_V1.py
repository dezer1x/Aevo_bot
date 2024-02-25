import logging
import requests
import telebot

logging.basicConfig(level=logging.INFO)
API_TOKEN = 'Bot_API_token'
bot = telebot.TeleBot(API_TOKEN)

def get_eth_data():
    url = "https://api.aevo.xyz/index?asset=ETH"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def get_alldata():
    url = "https://api.aevo.xyz/assets"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

waiting_for_request = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am the Helper bot for Aevo.\nType /help for a list of commands")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "All bot commands: \n/about - information about Aevo.\n/links - official links of Aevo.\n/assets - list of assets that are available for trading on Aevo.\n/price - view the price of assets.\n/funding - information about funding.", parse_mode='Markdown')

@bot.message_handler(commands=['assets'])
def send_assets(message):
    all_data = get_alldata()
    new_data = "\n".join(f"• {item}" for item in all_data)
    if all_data:
        bot.reply_to(message, new_data)
    else:
        bot.reply_to(message, "Error, try again!")

@bot.message_handler(commands=['about'])
def send_about(message):
    bot.reply_to(message, "Aevo is a high-performance decentralized derivatives exchange platform, focused on options and perpetual contracts, runs on a custom EVM roll-up that rolls up to Ethereum.", parse_mode='Markdown')

@bot.message_handler(commands=['links'])
def send_links(message):
    markup = telebot.types.InlineKeyboardMarkup()
    website = telebot.types.InlineKeyboardButton(text='Website', url='https://www.aevo.xyz/')
    twitter = telebot.types.InlineKeyboardButton(text='Twitter', url='https://twitter.com/aevoxyz')
    discord = telebot.types.InlineKeyboardButton(text='Discord', url='https://discord.com/invite/aevo')
    trading = telebot.types.InlineKeyboardButton(text='Trading', url='https://app.aevo.xyz/perpetual/eth')
    github = telebot.types.InlineKeyboardButton(text='Github', url='https://github.com/aevoxyz')
    markup.add(website, twitter, discord, trading, github)
    bot.reply_to(message, "Official AEVO links:", reply_markup=markup)

def get_crypto_price(asset):
  url = f"https://api.aevo.xyz/index?asset={asset}"
  response = requests.get(url)
  if response.status_code == 200:
      data = response.json()
      return data
  else:
      return None

@bot.message_handler(commands=['price'])
def send_price(message):
    command, *ticker = message.text.split()
    if not ticker:
        bot.reply_to(message, "Specify the asset ticker. For example: /price BTC")
        return

    asset = ticker[0].upper() 
    asset_price = get_crypto_price(asset)
    if asset_price:
        formatted_price = f"{asset} - {float(asset_price['price']):.2f}$"
        bot.reply_to(message, formatted_price)
    else:
        bot.reply_to(message, "Error, try again!")

def get_crypto_funding(asset):
  url = f"https://api.aevo.xyz/funding?instrument_name={asset}-PERP"
  response = requests.get(url)
  if response.status_code == 200:
      data = response.json()
      return data
  else:
      return None

@bot.message_handler(commands=['funding'])
def send_funding(message):
    command, *ticker = message.text.split()
    if not ticker:
        bot.reply_to(message, "Specify the asset ticker. For example: /price BTC")
        return

    asset = ticker[0].upper()
    asset_funding = get_crypto_funding(asset)
    if asset_funding:
        formatted_funding = f"{asset} - {float(asset_funding['funding_rate']):f}"
        bot.reply_to(message, formatted_funding)
    else:
        bot.reply_to(message, "Error, try again!")

if __name__ == '__main__':
    bot.polling(none_stop=True, skip_pending=True)

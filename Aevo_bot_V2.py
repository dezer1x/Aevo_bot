import logging
import requests
import telebot
import sqlite3
import schedule
import time
import threading

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
    user_language = get_user_language(message.chat.id) 
    if user_language in texts:
        bot.reply_to(message, texts[user_language]['welcome'])
    else:
        bot.reply_to(message, texts['en']['welcome']) 

@bot.message_handler(commands=['help'])
def send_help(message):
    user_language = get_user_language(message.chat.id)
    if user_language in texts:
        bot.reply_to(message, texts[user_language]['help'], parse_mode='Markdown')
    else:
        bot.reply_to(message, texts['en']['help'], parse_mode='Markdown')

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
    user_language = get_user_language(message.chat.id)
    if user_language in texts:
        bot.reply_to(message, texts[user_language]['about'], parse_mode='Markdown')
    else:
        bot.reply_to(message, texts['en']['about'], parse_mode='Markdown')

@bot.message_handler(commands=['links'])
def send_links(message):
    markup = telebot.types.InlineKeyboardMarkup()
    website = telebot.types.InlineKeyboardButton(text='Website', url='https://www.aevo.xyz/')
    twitter = telebot.types.InlineKeyboardButton(text='Twitter', url='https://twitter.com/aevoxyz')
    discord = telebot.types.InlineKeyboardButton(text='Discord', url='https://discord.com/invite/aevo')
    trading = telebot.types.InlineKeyboardButton(text='Trading', url='https://app.aevo.xyz/perpetual/eth')
    github = telebot.types.InlineKeyboardButton(text='Github', url='https://github.com/aevoxyz')
    markup.add(website, twitter, discord, trading, github)
    user_language = get_user_language(message.chat.id)
    if user_language in texts:
        bot.reply_to(message, texts[user_language]['links_message'], reply_markup=markup)
    else:
        bot.reply_to(message, texts['en']['links_message'], reply_markup=markup)

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
    user_language = get_user_language(message.chat.id)
    command, *ticker = message.text.split()
    if not ticker:
        if user_language in texts:
            bot.reply_to(message, texts[user_language]['price_error'])
        else:
            bot.reply_to(message, texts['en']['price_error'])
        return

    asset = ticker[0].upper() 
    asset_price = get_crypto_price(asset)
    if asset_price:
        formatted_price = f"{asset} - {float(asset_price['price']):.2f}$"
        bot.reply_to(message, formatted_price)
    else:
        if user_language in texts:
            bot.reply_to(message, texts[user_language]['error_try_again'])
        else:
            bot.reply_to(message, texts['en']['error_try_again'])

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
    user_language = get_user_language(message.chat.id)
    command, *ticker = message.text.split()
    if not ticker:
        if user_language in texts:
            bot.reply_to(message, texts[user_language]['funding_error'])
        else:
            bot.reply_to(message, texts['en']['funding_error'])
        return

    asset = ticker[0].upper()
    asset_funding = get_crypto_funding(asset)
    if asset_funding:
        formatted_funding = f"{asset} - {float(asset_funding['funding_rate']):f}"
        bot.reply_to(message, formatted_funding)
    else:
        if user_language in texts:
            bot.reply_to(message, texts[user_language]['error_try_again'])
        else:
            bot.reply_to(message, texts['en']['error_try_again'])

texts = {
    'en': {
        'welcome': "Hello! I am the Helper bot for Aevo.\nType /help for a list of commands",
        'help': "All bot commands: \n/about - information about Aevo.\n/links - official links of Aevo.\n/assets - list of assets that are available for trading on Aevo.\n/price - view the price of assets.\n/funding - information about funding.",
        'about': "Aevo is a high-performance decentralized derivatives exchange platform, focused on options and perpetual contracts, runs on a custom EVM roll-up that rolls up to Ethereum.",
        'price_error': "Specify the asset ticker. For example: /price BTC",
        'funding_error': "Specify the asset ticker. For example: /funding BTC",
        'error_try_again': "Error, try again!",
        'language_set': "Your language has been set to {0}",
        'links_message': "Official AEVO links:",
        'available_languages': "Available languages:\n🇬🇧 EN - English\n🇷🇺 RU - Russian\n🇪🇸 ES - Spanish\n🇺🇦 UA - Ukrainian\n🇫🇷 FR - French\n🇵🇱 PL - Polish\n🇮🇹 IT - Italian",
        'lang_error': "Please specify a language after the command. For example: /lang en",
        'unsupported_language': "Unsupported language.",
        'set_alert_long_error': "Invalid command format. Please use the following format: /set_alert_long [asset ticker] [target price]",
        'set_alert_long_success': "🟢Long alert set successfully.",
        'set_alert_short_error': "Invalid command format. Please use the following format: /set_alert_short [asset ticker] [target price]",
        'set_alert_short_success': "🔴Short alert set successfully.",
        'asset_not_found': "Asset not found.",
        'price_of': "🔴The price of",
        'fell_below_target': "has fallen below the target price of",
        'price_exceeded': "🟢The price of",
        'target_price': "has exceeded the target price of"
    },
    'ua': {
        'welcome': "Привіт! Я бот-помічник для Aevo.\nНапишіть /help, щоб отримати список доступних команд",
        'help': "Усі команди бота:\n/about - інформація про Aevo.\n/links - офіційні посилання на Aevo.\n/assets - список активів, доступних для торгівлі на Aevo.\n/price - перегляд ціни активів.\n/funding - інформація про фандинг.",
        'about': "Aevo - це високопродуктивна децентралізована платформа для обміну деривативами, орієнтована на опціони та безстрокові контракти, що працює на власному EVM roll-up, який розгортується на Ethereum.",
        'price_error': "Вкажіть тікер активу. Наприклад: /price BTC",
        'funding_error': "Вкажіть тікер активу. Наприклад: /funding BTC",
        'error_try_again': "Помилка, спробуйте ще раз!",
        'language_set': "Мова вашого бота була змінена на {0}",
        'links_message': "Офіційні посилання AEVO:",
        'available_languages': "Доступні мови:\n🇬🇧 EN - Англійська\n🇷🇺 RU - Російська\n🇪🇸 ES - Іспанська\n🇺🇦 UA - Українська\n🇫🇷 FR - Французька\n🇵🇱 PL - Польська\n🇮🇹 IT - Італійська",
        'lang_error': "Будь ласка, після команди введіть код мови. Наприклад: /lang ua",
        'unsupported_language': "Непідтримувана мова.",
        'set_alert_long_error': "Невірний формат команди. Використовуйте наступний формат: /set_alert_long [тікер активу] [цільова ціна]",
        'set_alert_long_success': "🟢Long оповіщення успішно встановлено.",
        'set_alert_short_error': "Невірний формат команди. Використовуйте наступний формат: /set_alert_short [тікер активу] [цільова ціна]",
        'set_alert_short_success': "🔴Short оповіщення успішно встановлено.",
        'asset_not_found': "Актив не знайдено.",
        'price_of': "🔴Ціна",
        'fell_below_target': "впала нижче цільової ціни",
        'price_exceeded': "🟢Ціна",
        'target_price': "перевищила цільову ціну"
    },
    'ru': {
        'welcome': "Привет! Я бот-помощник для Aevo.\nВведите /help, чтобы получить доступных список команд",
        'help': "Все команды бота:\n/about - информация о Aevo.\n/links - официальные ссылки на Aevo.\n/assets - список активов, доступных для торговли на Aevo.\n/price - просмотр цены активов.\n/funding - информация о фандинге.",
        'about': "Aevo - это высокопроизводительная децентрализованная платформа для обмена деривативами, ориентированная на опционы и бессрочные контракты, работающая на собственной платформе EVM, развернутой на Ethereum.",
        'price_error': "Укажите тикер актива. Например: /price BTC",
        'funding_error': "Укажите тикер актива. Например: /funding BTC",
        'error_try_again': "Ошибка, попробуйте снова!",
        'language_set': "Ваш язык установлен на {0}",
        'links_message': "Официальные ссылки AEVO:",
        'available_languages': "Доступные языки:\n🇬🇧 EN - Английский\n🇷🇺 RU - Русский\n🇪🇸 ES - Испанский\n🇺🇦 UA - Украинский\n🇫🇷 FR - Французский\n🇵🇱 PL - Польский\n🇮🇹 IT - Итальянский",
        'lang_error': "Пожалуйста, укажите язык после команды. Например: /lang ru",
        'unsupported_language': "Неподдерживаемый язык.",
        'set_alert_long_error': "Неверный формат команды. Пожалуйста, используйте следующий формат: /set_alert_long [тикер актива] [целевая цена]",
        'set_alert_long_success': "🟢Long оповещение успешно установлено.",
        'set_alert_short_error': "Неверный формат команды. Пожалуйста, используйте следующий формат: /set_alert_short [тикер актива] [целевая цена]",
        'set_alert_short_success': "🔴Short оповещение успешно установлено.",
        'asset_not_found': "Актив не найден.",
        'price_of': "🔴Цена",
        'fell_below_target': "упала ниже целевой цены",
        'price_exceeded': "🟢Цена",
        'target_price': "превысила целевую цену"
    },
    'es': {
        'welcome': "¡Hola! Soy el bot ayudante de Aevo.\nEscribe /help para obtener una lista de comandos",
        'help': "Todos los comandos del bot: \n/about - información sobre Aevo.\n/links - enlaces oficiales de Aevo.\n/assets - lista de activos disponibles para negociar en Aevo.\n/price - ver el precio de los activos.\n/funding - información sobre funding.",
        'about': "Aevo es una plataforma descentralizada de alto rendimiento para derivados, enfocada en opciones y contratos perpetuos, que se ejecuta en un roll-up EVM personalizado que se roll up a Ethereum.",
        'price_error': "Especifica el ticker del activo. Por ejemplo: /price BTC",
        'funding_error': "Especifica el ticker del activo. Por ejemplo: /funding BTC",
        'error_try_again': "Error, ¡inténtalo de nuevo!",
        'language_set': "Se ha establecido tu idioma en {0}",
        'links_message': "Enlaces oficiales AEVO:",
        'available_languages': "Idiomas disponibles:\n🇬🇧 EN - Inglés\n🇷🇺 RU - Ruso\n🇪🇸 ES - Español\n🇺🇦 UA - Ucraniano\n🇫🇷 FR - Francés\n🇵🇱 PL - Polaco\n🇮🇹 IT - Italiano",
        'lang_error': "Por favor, especifica un idioma después del comando. Por ejemplo: /lang es",
        'unsupported_language': "Idioma no compatible.",
        'set_alert_long_error': "Formato de comando no válido. Por favor, usa el siguiente formato: /set_alert_long [ticker de activo] [precio objetivo]",
        'set_alert_long_success': "🟢Alerta long configurada correctamente.",
        'set_alert_short_error': "Formato de comando no válido. Por favor, usa el siguiente formato: /set_alert_short [ticker de activo] [precio objetivo]",
        'set_alert_short_success': "🔴Alerta short configurada correctamente.",
        'asset_not_found': "Activo no encontrado.",
        'price_of': "🔴El precio de",
        'fell_below_target': "ha caído por debajo del precio objetivo de",
        'price_exceeded': "🟢El precio de",
        'target_price': "ha superado el precio objetivo de"
    },
    'fr': {
        'welcome': "Salut! Je suis le bot assistant d'Aevo.\nTapez /help pour obtenir une liste de commandes",
        'help': "Toutes les commandes du bot: \n/about - informations sur Aevo.\n/links - liens officiels d'Aevo.\n/assets - liste des actifs disponibles pour le trading sur Aevo.\n/price - voir le prix des actifs.\n/funding - informations sur le funding.",
        'about': "Aevo est une plateforme de trading de dérivés décentralisée à haute performance, axée sur les options et les contrats perpétuels, fonctionnant sur un roll-up EVM personnalisé qui se déploie sur Ethereum.",
        'price_error': "Spécifiez le ticker de l'actif. Par exemple: /price BTC",
        'funding_error': "Spécifiez le ticker de l'actif. Par exemple: /funding BTC",
        'error_try_again': "Erreur, réessayez!",
        'language_set': "Votre langue a été définie sur {0}",
        'links_message': "Liens officiels AEVO:",
        'available_languages': "Langues disponibles:\n🇬🇧 EN - Anglais\n🇷🇺 RU - Russe\n🇪🇸 ES - Espagnol\n🇺🇦 UA - Ukrainien\n🇫🇷 FR - Français\n🇵🇱 PL - Polonais\n🇮🇹 IT - Italien",
        'lang_error': "Veuillez spécifier une langue après la commande. Par exemple: /lang fr",
        'unsupported_language': "Langue non prise en charge.",
        'set_alert_long_error': "Format de commande invalide. Veuillez utiliser le format suivant: /set_alert_long [ticker d'actif] [prix cible]",
        'set_alert_long_success': "🟢Alerte long configurée avec succès.",
        'set_alert_short_error': "Format de commande invalide. Veuillez utiliser le format suivant: /set_alert_short [ticker d'actif] [prix cible]",
        'set_alert_short_success': "🔴Alerte short configurée avec succès.",
        'asset_not_found': "Actif non trouvé.",
        'price_of': "🔴Le prix de",
        'fell_below_target': "a chuté en dessous du prix cible de",
        'price_exceeded': "🟢Le prix de",
        'target_price': "a dépassé le prix cible de"
    },
    'pl': {
        'welcome': "Cześć! Jestem botem pomocnikiem dla Aevo.\nWpisz /help, aby uzyskać listę poleceń",
        'help': "Wszystkie polecenia bota: \n/about - informacje o Aevo.\n/links - oficjalne linki Aevo.\n/assets - lista aktywów dostępnych do handlu na Aevo.\n/price - wyświetl cenę aktywów.\n/funding - informacje o funding.",
        'about': "Aevo to wysokowydajna zdecentralizowana platforma do handlu instrumentami pochodnymi, skoncentrowana na opcjach i kontraktach terminowych, działająca na specjalnym EVM roll-up, który roll up do Ethereum.",
        'price_error': "Podaj ticker aktywa. Na przykład: /price BTC",
        'funding_error': "Podaj ticker aktywa. Na przykład: /funding BTC",
        'error_try_again': "Błąd, spróbuj ponownie!",
        'language_set': "Twoje ustawienie języka zostało zmienione na {0}",
        'links_message': "Oficjalne linki AEVO:",
        'available_languages': "Dostępne języki:\n🇬🇧 EN - Angielski\n🇷🇺 RU - Rosyjski\n🇪🇸 ES - Hiszpański\n🇺🇦 UA - Ukraiński\n🇫🇷 FR - Francuski\n🇵🇱 PL - Polski\n🇮🇹 IT - Włoski",
        'lang_error': "Proszę podać język po komendzie. Na przykład: /lang pl",
        'unsupported_language': "Nieobsługiwany język.",
        'set_alert_long_error': "Nieprawidłowy format komendy. Użyj następującego formatu: /set_alert_long [symbol aktywa] [cena docelowa]",
        'set_alert_long_success': "🟢Long powiadomienie ustawione pomyślnie.",
        'set_alert_short_error': "Nieprawidłowy format komendy. Użyj następującego formatu: /set_alert_short [symbol aktywa] [cena docelowa]",
        'set_alert_short_success': "🔴Short powiadomienie ustawione pomyślnie.",
        'asset_not_found': "Nie znaleziono aktywa.",
        'price_of': "🔴Cena",
        'fell_below_target': "spadła poniżej docelowej ceny",
        'price_exceeded': "🟢Cena",
        'target_price': "przekroczyła docelową cenę"
    },
    'it': {
        'welcome': "Ciao! Sono il bot assistente di Aevo.\nDigita /help per ottenere una lista di comandi",
        'help': "Tutti i comandi del bot: \n/about - informazioni su Aevo.\n/links - link ufficiali di Aevo.\n/assets - elenco degli asset disponibili per il trading su Aevo.\n/price - visualizza il prezzo degli asset.\n/funding - informazioni sul funding.",
        'about': "Aevo è una piattaforma decentralizzata ad alte prestazioni per derivati, focalizzata su opzioni e contratti perpetui, che funziona su un roll-up EVM personalizzato che si roll up su Ethereum.",
        'price_error': "Specifica il ticker dell'asset. Ad esempio: /price BTC",
        'funding_error': "Specifica il ticker dell'asset. Ad esempio: /funding BTC",
        'error_try_again': "Errore, riprova!",
        'language_set': "La tua lingua è stata impostata su {0}",
        'links_message': "Link ufficiali AEVO:",
        'available_languages': "Lingue disponibili:\n🇬🇧 EN - Inglese\n🇷🇺 RU - Russo\n🇪🇸 ES - Spagnolo\n🇺🇦 UA - Ucraino\n🇫🇷 FR - Francese\n🇵🇱 PL - Polacco\n🇮🇹 IT - Italiano",
        'lang_error': "Si prega di specificare una lingua dopo il comando. Ad esempio: /lang it",
        'unsupported_language': "Lingua non supportata.",
        'set_alert_long_error': "Formato del comando non valido. Usa il seguente formato: /set_alert_long [ticker dell'attività] [prezzo target]",
        'set_alert_long_success': "🟢Avviso long impostato correttamente.",
        'set_alert_short_error': "Formato del comando non valido. Usa il seguente formato: /set_alert_short [ticker dell'attività] [prezzo target]",
        'set_alert_short_success': "🔴Avviso short impostato correttamente.",
        'asset_not_found': "Attività non trovata.",
        'price_of': "🔴Il prezzo di",
        'fell_below_target': "è sceso al di sotto del prezzo target di",
        'price_exceeded': "🟢Il prezzo di",
        'target_price': "ha superato il prezzo target di"
    }
}

def save_user_language(user_id, language):
    conn = sqlite3.connect('aevo_bot.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)", (user_id, language))
    conn.commit()
    conn.close()

def get_user_language(user_id):
    conn = sqlite3.connect('aevo_bot.db')
    c = conn.cursor()
    c.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

@bot.message_handler(commands=['lang'])
def set_language(message):
    command, *language = message.text.split()
    if not language:
        user_language = get_user_language(message.chat.id)
        if user_language in texts:
            reply_message = texts[user_language]['lang_error'] + "\n" + texts[user_language]['available_languages']
            bot.reply_to(message, reply_message)
        else:
            reply_message = texts['en']['lang_error'] + "\n" + texts['en']['available_languages']
            bot.reply_to(message, reply_message)
        return

    user_language = language[0].lower()
    if user_language not in ['en', 'ua', 'ru', 'es', 'fr', 'pl', 'it']:
        user_language = get_user_language(message.chat.id)
        if user_language in texts:
            reply_message = texts[user_language]['unsupported_language'] + "\n" + texts[user_language]['available_languages']
            bot.reply_to(message, reply_message)
        else:
            reply_message = texts['en']['unsupported_language'] + "\n" + texts['en']['available_languages']
            bot.reply_to(message, reply_message)
        return

    save_user_language(message.chat.id, user_language)
    if user_language in texts:
        bot.reply_to(message, texts[user_language]['language_set'].format(user_language.upper()))
    else:
        bot.reply_to(message, texts['en']['language_set'].format(user_language.upper()))

def get_crypto_price(asset):
    url = f"https://api.aevo.xyz/index?asset={asset}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

@bot.message_handler(commands=['set_alert_long'])
def set_alert_long(message):
    command, *args = message.text.split()
    user_language = get_user_language(message.chat.id)
    if len(args) != 2:
        if user_language in texts:
            bot.reply_to(message, texts[user_language]['set_alert_long_error'])
        else:
            bot.reply_to(message, texts['en']['set_alert_long_error'])
        return

    asset, target_price = args[0].upper(), args[1]
    if check_asset_exists(asset):
        conn = sqlite3.connect('aevo_bot.db')
        c = conn.cursor()
        c.execute("INSERT INTO alerts (user_id, asset, target_price) VALUES (?, ?, ?)", (message.chat.id, asset, target_price))
        conn.commit()
        conn.close()
        if user_language in texts:
            bot.reply_to(message, texts[user_language]['set_alert_long_success'])
        else:
            bot.reply_to(message, texts['en']['set_alert_long_success'])
    else:
        if user_language in texts:
            bot.reply_to(message, texts[user_language]['asset_not_found'])
        else:
            bot.reply_to(message, texts['en']['asset_not_found'])

@bot.message_handler(commands=['set_alert_short'])
def set_alert_short(message):
    command, *args = message.text.split()
    user_language = get_user_language(message.chat.id)
    if len(args) != 2:
        if user_language in texts:
            bot.reply_to(message, texts[user_language]['set_alert_short_error'])
        else:
            bot.reply_to(message, texts['en']['set_alert_short_error'])
        return

    asset, target_price = args[0].upper(), args[1]
    if check_asset_exists(asset):
        conn = sqlite3.connect('aevo_bot.db')
        c = conn.cursor()
        c.execute("INSERT INTO short_alerts (user_id, asset, target_price) VALUES (?, ?, ?)", (message.chat.id, asset, target_price))
        conn.commit()
        conn.close()
        if user_language in texts:
            bot.reply_to(message, texts[user_language]['set_alert_short_success'])
        else:
            bot.reply_to(message, texts['en']['set_alert_short_success'])
    else:
        if user_language in texts:
            bot.reply_to(message, texts[user_language]['asset_not_found'])
        else:
            bot.reply_to(message, texts['en']['asset_not_found'])

def check_asset_exists(asset):
    asset_price = get_crypto_price(asset)
    return asset_price is not None

def create_alerts_table():
    conn = sqlite3.connect('aevo_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    asset TEXT,
                    target_price REAL
                )''')
    conn.commit()
    conn.close()

def create_short_alerts_table():
    conn = sqlite3.connect('aevo_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS short_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                asset TEXT,
                target_price REAL
            )''')
    conn.commit()
    conn.close()

def check_price_alerts():
    check_long_alerts()
    check_short_alerts()

def check_long_alerts():
  conn = sqlite3.connect('aevo_bot.db')
  c = conn.cursor()
  c.execute("SELECT user_id, asset, target_price FROM alerts")
  alerts = c.fetchall()
  conn.close()

  for alert in alerts:
      user_id, asset, target_price = alert
      asset_price = get_crypto_price(asset)
      if asset_price and float(asset_price['price']) >= float(target_price):
          user_language = get_user_language(user_id)
          if user_language in texts:
              response_message = f"{texts[user_language]['price_exceeded']} {asset} {texts[user_language]['target_price']} {target_price}!"
          else:
              response_message = f"{texts['en']['price_exceeded']} {asset} {texts['en']['target_price']} {target_price}!"
          bot.send_message(user_id, response_message)
          conn = sqlite3.connect('aevo_bot.db')
          c = conn.cursor()
          c.execute("DELETE FROM alerts WHERE user_id=? AND asset=? AND target_price=?", (user_id, asset, target_price))
          conn.commit()
          conn.close()

def check_short_alerts():
  conn = sqlite3.connect('aevo_bot.db')
  c = conn.cursor()
  c.execute("SELECT user_id, asset, target_price FROM short_alerts")
  alerts = c.fetchall()
  conn.close()

  for alert in alerts:
      user_id, asset, target_price = alert
      asset_price = get_crypto_price(asset)
      if asset_price and float(asset_price['price']) <= float(target_price):
          user_language = get_user_language(user_id)
          response_message = f"The price of {asset} has fallen below the target price of {target_price}!"
          if user_language in texts:
              response_message = f"{texts[user_language]['price_of']} {asset} {texts[user_language]['fell_below_target']} {target_price}!"
          else:
              response_message = f"{texts['en']['price_of']} {asset} {texts['en']['fell_below_target']} {target_price}!"

          bot.send_message(user_id, response_message)
          conn = sqlite3.connect('aevo_bot.db')
          c = conn.cursor()
          c.execute("DELETE FROM short_alerts WHERE user_id=? AND asset=? AND target_price=?", (user_id, asset, target_price))
          conn.commit()
          conn.close()

def run_scheduler():
    schedule.every(5).seconds.do(check_price_alerts)
    while True:
        schedule.run_pending()
        time.sleep(1)

create_alerts_table()
create_short_alerts_table()

scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

if __name__ == '__main__':
    bot.polling(none_stop=True, skip_pending=True)

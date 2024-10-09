import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot API Token and TON API Details
API_TOKEN = '8011295923:AAHs3WFtZuy4C7kE5OoGhkFnYLjJNdUQhuM'
TONCENTER_API_KEY = 'c51eb2512ff20a773d677f9b0e0ce9c1b6a4df82f31d7f47dd51dece0a483745'
TONCENTER_API_URL = 'https://toncenter.com/api/v2'

bot = telebot.TeleBot(API_TOKEN)

menu_state = {}

# Entres ton adresse TON pour vérifier le solde
def get_wallet_balance(wallet_address):
    url = f"{TONCENTER_API_URL}/getAddressInformation"
    params = {
        'address': wallet_address,
        'api_key': TONCENTER_API_KEY
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            balance_ton = int(data['result']['balance']) / 10**9  # Convertion en TON
            return f"Wallet Balance: {balance_ton} TON"
        else:
            return "Error retrieving wallet information"
    else:
        return f"Error {response.status_code}: {response.text}"


@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    menu_state[chat_id] = 'main_menu'
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Paiement", callback_data='payment'),
        InlineKeyboardButton("Vérifier Solde", callback_data='check_balance'),
        InlineKeyboardButton("Annuler", callback_data='cancel')
    )

    welcome_message = "Bienvenue !\nSélectionnez une option :"
    bot.send_message(chat_id, welcome_message, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    chat_id = call.message.chat.id
    data = call.data
    
    current_state = menu_state.get(chat_id, 'main_menu')

    if data == 'payment':
        bot.send_message(chat_id, "Vous avez sélectionné: Effectuer un paiement.\nVeuillez entrer votre adresse TON :")
        menu_state[chat_id] = 'payment'
    elif data == 'check_balance':
        bot.send_message(chat_id, "Veuillez entrer votre adresse TON pour vérifier le solde :")
        menu_state[chat_id] = 'check_balance'
    elif data == 'cancel':
        bot.send_message(chat_id, "Opération annulée.")
        menu_state[chat_id] = 'main_menu'
    else:
        bot.send_message(chat_id, "Option invalide.")

@bot.message_handler(func=lambda message: True)
def handle_text_menu(message):
    chat_id = message.chat.id
    user_input = message.text.strip()

    if chat_id not in menu_state:
        bot.send_message(chat_id, "Veuillez d'abord taper /start pour afficher le menu.")
        return

    current_state = menu_state[chat_id]

    if current_state == 'payment':
        ton_address = user_input
        bot.send_message(chat_id, f"Effectuer un paiement à l'adresse : {ton_address}\n\nPour finaliser, envoyez le montant et le hash de la transaction.")
        menu_state[chat_id] = 'main_menu'

    elif current_state == 'check_balance':
        ton_address = user_input
        bot.send_message(chat_id, f"Vérification du solde pour l'adresse: {ton_address}...")
        balance_info = get_wallet_balance(ton_address)
        bot.send_message(chat_id, balance_info)
        menu_state[chat_id] = 'main_menu'

bot.polling()

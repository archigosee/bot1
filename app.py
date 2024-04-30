import os
import logging
import telebot
from flask import Flask, render_template, session, request, redirect, url_for
from telebot import types

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Initialize telebot
bot = telebot.TeleBot('6677929385:AAHBw5DCcRIEOhh5XIgQpwOhZqUS4b7O5ss')


# Define Flask routes
@app.route('/')
def index():
    user_id = session.get('user_id')
    print("User ID:", user_id)  # Add this line to check if user_id is correctly received

    return render_template('index.html', user_id=user_id)


@app.route('/checkout')
def checkout():
    cart_items = session.get('cart', [])
    total_price = sum(item['price'] for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    item = {'name': data['name'], 'price': data['price']}
    session.setdefault('cart', []).append(item)
    return 'Item added to cart!'


@app.route('/process_checkout', methods=['POST'])
def process_checkout():
    session['cart'] = []
    return 'Checkout completed!'


# Define telebot webhook route
@app.route('/webhook', methods=['POST'])
def webhook_handler():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    logging.debug("Received update: %s", update)

    if update.message and update.message.text == '/start':
        logging.debug("Received /start command")
        handle_start(update.message)

    return '', 200


def handle_start(message):
    print("Handling start command...")
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    welcome_message = (f"Hello, {user_name}! Welcome to the bot. Your user ID is {user_id}. Would you like to continue "
                       f"registering or visit our website?")

    markup = types.InlineKeyboardMarkup()
    website_btn = types.InlineKeyboardButton('Visit Website', url='http://127.0.0.1:5000/')
    markup.add(website_btn)

    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)

    # Set the user ID in the session
    session['user_id'] = user_id

    # Redirect to the / route
    return redirect(url_for('index'))


# Set up telebot webhook
WEBHOOK_URL = 'https://2502-196-188-35-100.ngrok-free.app'  # Replace with your ngrok URL
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL + '/webhook')

# Start Flask app
if __name__ == '__main__':
    app.run(debug=True)

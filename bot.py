import telebot
from telebot import types
from config import TOKEN, POSTER_TOKEN
from db import init_db, add_or_update_user, get_user
from api_client import Client
import logging
from new_check_monitor import run_monitor
from threading import Thread

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Инициализация
client = Client(POSTER_TOKEN)
bot = telebot.TeleBot(TOKEN)
init_db()


# Главное меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("👤 Мій профіль"))
    return markup


# Старт
@bot.message_handler(commands=['start'])
def start(message):
    logging.info(f"/start від user_id={message.chat.id}")
    user = get_user(message.chat.id)
    if user:
        bot.send_message(message.chat.id, "Ви вже зареєстровані.", reply_markup=main_menu())
        logging.info(f"Повторна спроба реєстрації: {user}")
    else:
        bot.send_message(message.chat.id, "Вітаю! Як вас звати?")
        bot.register_next_step_handler(message, get_name)


# Получение имени
def get_name(message):
    name = message.text.strip()
    logging.info(f"Отримано ім'я від user_id={message.chat.id}: {name}")
    bot.send_message(message.chat.id, "Будь ласка, поділіться своїм номером телефону:", reply_markup=phone_keyboard())
    bot.register_next_step_handler(message, get_phone, name)


# Кнопка для отправки телефона
def phone_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("📱 Надіслати номер", request_contact=True)
    markup.add(button)
    return markup


# Получение телефона
def get_phone(message, name):
    user_id = message.chat.id

    if message.contact and message.contact.phone_number.startswith("38"):
        phone = "+" + message.contact.phone_number
    elif message.text and message.text.startswith("+38"):
        phone = message.text.strip()
    else:
        bot.send_message(user_id, "Номер має починатися з +38. Спробуйте ще раз.")
        logging.warning(f"Невірний номер від user_id={user_id}: {message.text}")
        bot.register_next_step_handler(message, get_phone, name)
        return

    logging.info(f"Отримано номер телефону від user_id={user_id}: {phone}")

    try:
        existing_info = client.get_client_by_phone(phone)
        if existing_info:
            poster_id = existing_info['client_id']
            logging.info(f"Використано існуючого клієнта: poster_id={poster_id} для user_id={user_id}")
        else:
            crm_response = client.create_new_client(name, phone)
            print(crm_response)
            poster_id = crm_response['response']  # ← отриманий poster_id
            logging.info(f"Створено клієнта в CRM: poster_id={poster_id} для user_id={user_id}")
    except Exception as e:
        logging.error(f"Помилка створення клієнта в CRM: {e}")
        bot.send_message(user_id, "Сталася помилка при збереженні у CRM. Спробуйте пізніше.")
        return

    add_or_update_user(user_id, poster_id, name=name, phone=phone)
    bot.send_message(user_id, "Реєстрацію завершено успішно!", reply_markup=main_menu())


# Обработка "Мій профіль"
@bot.message_handler(func=lambda m: m.text == "👤 Мій профіль")
def profile(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if user:
        try:
            crm_data = client.get_client_by_id(user["poster_id"])
            bonuses = crm_data.get("bonus", 0)
            msg = (
                f"👤 Ваш профіль:\n\n"
                f"📛 Ім'я: {user['name']}\n"
                f"📞 Телефон: {user['phone']}\n"
                f"🎁 Бонуси: {bonuses}\n"
                # f"🆔 Poster ID: {user["poster_id"]}"
            )
            logging.info(f"Профіль запрошено user_id={user_id}")
            bot.send_message(user_id, msg)
        except Exception as e:
            logging.error(f"Помилка отримання даних з CRM для user_id={user_id}: {e}")
            bot.send_message(user_id, "Не вдалося отримати дані з CRM.")
    else:
        logging.info(f"Спроба перегляду профілю незареєстрованим користувачем user_id={user_id}")
        bot.send_message(user_id, "Вас не знайдено в базі. Натисніть /start для реєстрації.")


if __name__ == "__main__":
    # Запуск бота
    monitor_thread = Thread(target=run_monitor, args=(10,), daemon=True)
    monitor_thread.start()
    bot.polling()

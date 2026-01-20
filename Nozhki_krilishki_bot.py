import telebot
import time
import os

# === НАСТРОЙКИ ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_CHAT_ID = "786368933"

# Создаем бота с увеличенными таймаутами
bot = telebot.TeleBot(TOKEN, threaded=True)

# === МЕНЮ ===
menu_categories = {
    "🍗 Ножки": {
        "Ножка оригинальная 1 шт (120г.) - 165₽": 165,
        "Ножка острая 1 шт (120г.) - 165₽": 165,
        "Ножка Терияки 1 шт (120г.) - 195₽": 195,
        "Ножка Терияки острая 1 шт (120г.) - 195₽": 195,
        "Ножка Кисло-сладкая 1 шт (120г.) - 205₽": 205,
        "Ножка Кисло-сладкая острая 1 шт (120г.) - 205₽": 205,
        "Ножка Апельсин-облепиха 1 шт (120г.) - 215₽": 215,
        "Ножка Апельсин-облепиха острая 1 шт (120г.) - 215₽": 215,
        "Ножка «Очень острая» 1 шт (120г.) - 240₽": 240
    },
    "🥓 Крылышки": {
        "Крылышки оригинальные 3 шт (180г.) - 260₽": 260,
        "Крылышки острые 3 шт (180г.) - 260₽": 260,
        "Крылышки Терияки 3 шт (180г.) - 275₽": 275,
        "Крылышки Терияки острые 3 шт (180г.) - 275₽": 275,
        "Крылышки Кисло-сладкие 3 шт (180г.) - 285₽": 285,
        "Крылышки Кисло-сладкие острые 3 шт (180г.) - 285₽": 285,
        "Крылышки Апельсин-облепиха 3 шт (180г.) - 290₽": 290,
        "Крылышки Апельсин-облепиха острые 3 шт (180г.) - 290₽": 290,
        "Крылышки «Очень острые» 3 шт (120г.) - 300₽": 300
    },
    "🍖 Стрипсы": {
        "Стрипсы оригинальные 3 шт (120г.) - 270₽": 270,
        "Стрипсы острые 3 шт (120г.) - 270₽": 270
    },
    "🍟 Фри": {
        "Картофель фри (70 г) - 145₽": 145,
        "Картофель по-деревенски (70 г) - 155₽": 155,
        "Фрикадельки куриные 9 шт - 330₽": 330,
        "Картофельные бочонки (100 г) - 240₽": 240,
        "Сырные палочки 9 шт - 430₽": 430
    },
    "🍔 Бургеры": {
        "Чикен бургер (300г.) - 310₽": 310,
        "Чикен бургер острый (300г.) - 310₽": 310,
        "Бургер «Тар-тар» (300г.) - 550₽": 550,
        "Бургер «Фирменный» (300г.) - 540₽": 540,
        "Бургер «Властелин колец» (320г.) - 560₽": 560
    },
    "🌭 Хот-доги": {
        "Хот-дог классический (250г.) - 240₽": 240,
        "Хот-дог классический двойной (310г.) - 290₽": 290,
        "Хот-дог «Джон» (270г.) - 270₽": 270,
        "Хот-дог «Джон» двойной (320г.) - 430₽": 430
    },
    "🥫Соусы": {
        "Чесночный - 70₽": 70,
        "Барбекю - 70₽": 70,
        "Сырный - 70₽": 70,
        "Кетчуп - 70₽": 70
    },
    "🥤 Напитки": {
        "Чай зеленый 0.25л - 50₽": 50,
        "Чай черный 0.25л - 50₽": 50,
        "Чай зеленый 0.35л - 60₽": 60,
        "Чай черный 0.35л - 60₽": 60,
        "Чай брусничный 0.3л - 89₽": 89,
        "Добрый 0.2л в ассортименте - 60₽": 60,
    }
}

# === ХРАНЕНИЕ ДАННЫХ ===
order_state = {}  # для этапов оформления заказа: "waiting_name", "waiting_phone", "waiting_address"
current_category = {}  # для отслеживания, в какой категории находится пользователь
user_data = {}  # данные клиента: имя, телефон, адрес
cart = {}  # корзина: {chat_id: {"Ножка оригинальная": 2, ...}}


# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
def reset_user(chat_id):
    """Очистить все данные пользователя"""
    order_state.pop(chat_id, None)
    current_category.pop(chat_id, None)
    user_data.pop(chat_id, None)
    cart.pop(chat_id, None)


def get_main_menu():
    """Главное меню с категориями в виде кнопок"""
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    # Создаем кнопки для каждой категории
    for category in menu_categories.keys():
        markup.add(telebot.types.KeyboardButton(category))

    # Добавляем кнопки "Меню" и "Вызвать главное меню" в один ряд
    markup.row(
        telebot.types.KeyboardButton("📱 Меню"),
        telebot.types.KeyboardButton("Вызвать главное меню")
    )

    # Добавляем кнопку корзины
    markup.add(telebot.types.KeyboardButton("🛒 Корзина"))

    return markup


def get_category_menu(category):
    """Меню с блюдами конкретной категории"""
    items = menu_categories[category]
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    # Добавляем каждый товар как отдельную кнопку
    for item in items:
        markup.add(telebot.types.KeyboardButton(item))

    # Кнопки навигации
    markup.row(
        telebot.types.KeyboardButton("⬅️ Назад"),
        telebot.types.KeyboardButton("📱 Меню")
    )
    markup.add(telebot.types.KeyboardButton("🛒 Корзина"))

    return markup


def cancel_or_home_markup():
    """Клавиатура с отменой и возвратом в меню"""
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(
        telebot.types.KeyboardButton("❌ Отменить заказ"),
        telebot.types.KeyboardButton("Меню")
    )
    markup.add(telebot.types.KeyboardButton("Вызвать главное меню"))
    return markup


# === ОСНОВНЫЕ КОМАНДЫ ===
@bot.message_handler(commands=['start'])
def start_command(m):
    chat_id = m.chat.id
    reset_user(chat_id)

    welcome_text = (
        "👋 Добро пожаловать в *Ножки крылышки*!\n\n"
        "*Доступные категории:*"
    )

    # Формируем список категорий
    categories_list = ""
    for i, category in enumerate(menu_categories.keys(), 1):
        categories_list += f"{i}. {category}\n"

    try:
        bot.send_message(
            chat_id,
            f"{welcome_text}\n\n{categories_list}\n\nВыберите категорию:",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


@bot.message_handler(func=lambda m: m.text in ["📱 Меню", "Вызвать главное меню"])
def menu_command(m):
    chat_id = m.chat.id

    welcome_text = (
        "👋 Добро пожаловать в *Ножки крылышки*!\n\n"
        "*Доступные категории:*"
    )

    # Формируем список категорий
    categories_list = ""
    for i, category in enumerate(menu_categories.keys(), 1):
        categories_list += f"{i}. {category}\n"

    try:
        bot.send_message(
            chat_id,
            f"{welcome_text}\n\n{categories_list}\n\nВыберите категорию:",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


# === ВЫБОР КАТЕГОРИИ ===
@bot.message_handler(func=lambda m: m.text in menu_categories)
def show_category(m):
    chat_id = m.chat.id
    category = m.text
    current_category[chat_id] = category

    # Формируем список блюд в категории
    items = menu_categories[category]
    items_text = f"*{category}*\n\n"

    for i, (item_name, price) in enumerate(items.items(), 1):
        items_text += f"{i}. {item_name}\n"

    try:
        bot.send_message(
            chat_id,
            f"{items_text}\nВыберите блюдо:",
            reply_markup=get_category_menu(category),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


# === ВЫБОР БЛЮДА ИЗ КАТЕГОРИИ ===
@bot.message_handler(func=lambda m: any(m.text in items for items in menu_categories.values()))
def add_item_from_category(m):
    chat_id = m.chat.id
    item_name = m.text

    # Находим категорию и цену
    price = None
    item_category = None
    for cat, items in menu_categories.items():
        if item_name in items:
            price = items[item_name]
            item_category = cat
            break

    if price is None:
        try:
            bot.send_message(chat_id, "Блюдо не найдено. Выберите из меню.", reply_markup=get_main_menu())
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
        return

    # Добавляем в корзину
    if chat_id not in cart:
        cart[chat_id] = {}
    cart[chat_id][item_name] = cart[chat_id].get(item_name, 0) + 1

    # Возвращаемся в ту же категорию с подтверждением
    items = menu_categories[item_category]
    items_text = f"*{item_category}*\n\n"

    for i, (name, price) in enumerate(items.items(), 1):
        items_text += f"{i}. {name}\n"

    try:
        bot.send_message(
            chat_id,
            f"✅ *{item_name}*\nДобавлен(а) в корзину!\n\n{items_text}\nВыберите блюдо:",
            reply_markup=get_category_menu(item_category),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


# === КНОПКА "НАЗАД" ===
@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def back_to_categories(m):
    try:
        bot.send_message(
            m.chat.id,
            "Выберите категорию:",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


# === КОРЗИНА ===
@bot.message_handler(func=lambda m: m.text == "🛒 Корзина")
def show_cart(m):
    chat_id = m.chat.id
    if chat_id not in cart or not cart[chat_id]:
        try:
            bot.send_message(
                chat_id,
                "🛒 *Ваша корзина пуста* 😢\n\nВыберите блюда из меню.",
                reply_markup=get_main_menu(),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
        return

    total = 0
    text = "🛒 *Ваш заказ:*\n\n"
    for item, count in cart[chat_id].items():
        # Находим цену товара
        item_price = None
        for cat_items in menu_categories.values():
            if item in cat_items:
                item_price = cat_items[item]
                break

        if item_price is None:
            continue

        price = item_price * count
        total += price
        text += f"• {item} ×{count} — {price} руб\n"
    text += f"\n*Итого: {total} руб*"

    inline_markup = telebot.types.InlineKeyboardMarkup()
    inline_markup.row(
        telebot.types.InlineKeyboardButton("✅ Оформить заказ", callback_data="confirm_order"),
        telebot.types.InlineKeyboardButton("🔄 Очистить корзину", callback_data="clear_cart")
    )

    try:
        bot.send_message(
            chat_id,
            text,
            reply_markup=inline_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


# === ОЧИСТКА КОРЗИНЫ ===
@bot.callback_query_handler(func=lambda call: call.data == "clear_cart")
def clear_cart_callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if chat_id in cart:
        cart[chat_id] = {}

    try:
        bot.answer_callback_query(call.id, "Корзина очищена")
        bot.edit_message_text(
            "🛒 *Корзина очищена* ✅",
            chat_id,
            message_id,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка при редактировании сообщения: {e}")

    try:
        bot.send_message(
            chat_id,
            "🛒 *Корзина очищена*\n\nВыберите блюда из меню:",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


# === НАЧАЛО ОФОРМЛЕНИЯ ===
@bot.callback_query_handler(func=lambda call: call.data == "confirm_order")
def confirm_order(call):
    chat_id = call.message.chat.id
    if not cart.get(chat_id):
        try:
            bot.answer_callback_query(call.id, "Корзина пуста!", show_alert=True)
        except Exception as e:
            print(f"Ошибка при ответе на callback: {e}")
        return

    order_state[chat_id] = "waiting_name"

    try:
        # Скрываем inline-клавиатуру
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
    except:
        pass

    try:
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id,
            "👤 *Введите ваше имя:*",
            reply_markup=cancel_or_home_markup(),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


# === ОБРАБОТКА ТЕКСТА ===
@bot.message_handler(func=lambda m: True)
def handle_text(m):
    chat_id = m.chat.id
    text = m.text.strip()

    # Обработка кнопок отмены и меню
    if text == "❌ Отменить заказ":
        reset_user(chat_id)
        try:
            bot.send_message(
                chat_id,
                "❌ *Заказ отменён*\n\nВы в главном меню:",
                reply_markup=get_main_menu(),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
        return

    if text in ["📱 Меню", "Вызвать главное меню"]:
        menu_command(m)
        return

    current_state = order_state.get(chat_id)

    # Этап: ввод имени
    if current_state == "waiting_name":
        if not text:
            try:
                bot.send_message(chat_id, "Пожалуйста, введите ваше имя:")
            except Exception as e:
                print(f"Ошибка при отправке сообщения: {e}")
            return

        user_data[chat_id] = {"name": text}
        order_state[chat_id] = "waiting_phone"

        # Кнопка для отправки контакта
        contact_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        contact_markup.add(telebot.types.KeyboardButton("📱 Отправить номер", request_contact=True))
        contact_markup.row(
            telebot.types.KeyboardButton("❌ Отменить заказ"),
            telebot.types.KeyboardButton("Меню")
        )
        contact_markup.add(telebot.types.KeyboardButton("Вызвать главное меню"))

        try:
            bot.send_message(
                chat_id,
                "📞 *Введите номер телефона:*\n\nНажмите кнопку ниже, чтобы отправить номер автоматически,\nили введите его вручную (например, +79991234567):",
                reply_markup=contact_markup,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")

    # Этап: ввод телефона (ТЕКСТОМ)
    elif current_state == "waiting_phone":
        # Простая проверка: оставляем только цифры
        digits_only = ''.join(filter(str.isdigit, text))
        if len(digits_only) >= 10:  # минимум 10 цифр (для РФ и большинства стран)
            user_data[chat_id]["phone"] = text  # сохраняем как есть (с форматированием)
            order_state[chat_id] = "waiting_address"
            try:
                bot.send_message(
                    chat_id,
                    "🏠 *Введите адрес доставки:*",
                    reply_markup=cancel_or_home_markup(),
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Ошибка при отправке сообщения: {e}")
        else:
            # Неверный формат
            try:
                bot.send_message(
                    chat_id,
                    "📞 Пожалуйста, введите корректный номер телефона (например, +79991234567) или нажмите кнопку «📱 Отправить номер».",
                    reply_markup=cancel_or_home_markup()
                )
            except Exception as e:
                print(f"Ошибка при отправке сообщения: {e}")

    # Этап: ввод адреса
    elif current_state == "waiting_address":
        if not text:
            try:
                bot.send_message(chat_id, "Пожалуйста, введите адрес доставки:")
            except Exception as e:
                print(f"Ошибка при отправке сообщения: {e}")
            return

        user_data[chat_id]["address"] = text
        order_state[chat_id] = None

        try:
            send_order_to_owner(chat_id)
        except Exception as e:
            print(f"Ошибка при отправке заказа владельцу: {e}")

        reset_user(chat_id)

        try:
            bot.send_message(
                chat_id,
                "🎉 *Спасибо за заказ!*\n\nМенеджер свяжется с вами в ближайшее время, чтобы подтвердить заказ.",
                reply_markup=get_main_menu(),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")

    # Вне процесса оформления — направляем в меню
    else:
        try:
            bot.send_message(
                chat_id,
                "Выберите действие из меню:",
                reply_markup=get_main_menu()
            )
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")


# === ОБРАБОТКА КОНТАКТА ===
@bot.message_handler(content_types=['contact'])
def handle_contact(m):
    chat_id = m.chat.id
    if order_state.get(chat_id) == "waiting_phone":
        user_data[chat_id]["phone"] = m.contact.phone_number
        order_state[chat_id] = "waiting_address"

        try:
            bot.send_message(
                chat_id,
                "🏠 *Введите адрес доставки:*",
                reply_markup=cancel_or_home_markup(),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
    else:
        try:
            bot.send_message(
                chat_id,
                "Спасибо! Но сейчас я не запрашиваю номер.\n\nВыберите действие:",
                reply_markup=get_main_menu()
            )
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")


# === ОТПРАВКА ЗАКАЗА ВЛАДЕЛЬЦУ ===
def send_order_to_owner(chat_id):
    client = user_data[chat_id]
    order_items = cart[chat_id]

    msg = "🆕 *НОВЫЙ ЗАКАЗ!*\n\n"
    msg += f"👤 *Имя:* {client['name']}\n"
    msg += f"📱 *Телефон:* {client['phone']}\n"
    msg += f"🏠 *Адрес:* {client['address']}\n\n"
    msg += "*Состав заказа:*\n"

    total = 0
    for item, count in order_items.items():
        # Находим цену товара
        item_price = None
        for cat_items in menu_categories.values():
            if item in cat_items:
                item_price = cat_items[item]
                break

        if item_price is None:
            continue

        price = item_price * count
        total += price
        msg += f"  • {item} ×{count} — {price} руб\n"

    msg += f"\n*ИТОГО: {total} руб*"

    try:
        bot.send_message(OWNER_CHAT_ID, msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка при отправке заказа владельцу: {e}")


# === ЗАПУСК БОТА С ПОВТОРАМИ ПРИ ОШИБКАХ ===
def run_bot():
    print("🤖 Бот 'Ножки крылышки' запускается...")

    while True:
        try:
            print("🔄 Подключаемся к Telegram API...")
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            print(f"⚠️ Ошибка подключения: {e}")
            print("⏳ Повторная попытка через 10 секунд...")
            time.sleep(10)


# === ЗАПУСК ===
if __name__ == "__main__":
    run_bot()
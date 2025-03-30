import telebot
from telebot import types
import random
import requests
import time

TOKEN = "7873610003:AAFUWEIYvVpHqlwuozH8zgG0L8KmXUsAGhg"

bot = telebot.TeleBot(TOKEN)

def luhn(card_number):
    digits = [int(digit) for digit in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = 0
    total += sum(odd_digits)
    for digit in even_digits:
        total += sum(divmod(digit * 2, 10))
    return total % 10 == 0

def generate_credit_card(bin_number, length):
    while True:
        card_number = bin_number + ''.join(random.choice('0123456789') for _ in range(length - len(bin_number) - 1))
        check_digit = (10 - sum(int(d) for d in card_number[::2] + ''.join(str(sum(divmod(int(d) * 2, 10))) for d in card_number[1::2])) % 10) % 10
        card_number += str(check_digit)
        if luhn(card_number):
            return card_number

def generate_credit_cards(count, bin_number=None, length=None):
    cards = []
    for _ in range(count):
        if not bin_number:
            bin_number = random.choice(['4', '5', '6', '37'])
        if not length:
            length = random.choice([15, 16])
        card_number = generate_credit_card(bin_number, length)
        cvv = ''.join(random.choice('0123456789') for _ in range(3))
        expiry_month = str(random.randint(1, 12)).zfill(2)
        expiry_year = str(random.randint(24, 29))
        cards.append(f"{card_number}|{expiry_month}|{expiry_year}|{cvv}")
    return cards

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    credit_card_button = types.InlineKeyboardButton("Kredi Kartı Modu", callback_data="credit_card")
    markup.add(credit_card_button)
    bot.send_message(message.chat.id, "Selam! Kredi kartı moduna hoş geldin! 😈", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "credit_card")
def credit_card_menu(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    random_button = types.InlineKeyboardButton("Rastgele Oluştur", callback_data="cc_random")
    selected_button = types.InlineKeyboardButton("Seçilen Özelliklere Göre Oluştur", callback_data="cc_selected")
    cc_checker_button = types.InlineKeyboardButton("CC Checker", callback_data="cc_checker")
    markup.add(random_button, selected_button, cc_checker_button)
    bot.send_message(call.message.chat.id, "Kredi kartı modunda ne yapmak istersin?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "cc_random")
def cc_random(call):
    bot.send_message(call.message.chat.id, "Kaç adet kart oluşturulacak?")
    bot.register_next_step_handler(call.message, generate_random_cards_handler)

def generate_random_cards_handler(message):
    try:
        count = int(message.text)
        cards = generate_credit_cards(count)
        with open("H#shtaginc kartlar.txt", "w") as f:
            f.write("\n".join(cards))
        with open("H#shtaginc kartlar.txt", "rb") as f:
            bot.send_document(message.chat.id, f)
    except ValueError:
        bot.send_message(message.chat.id, "Geçersiz sayı girişi!")

@bot.callback_query_handler(func=lambda call: call.data == "cc_selected")
def cc_selected(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    visa_button = types.InlineKeyboardButton("Visa", callback_data="visa")
    mastercard_button = types.InlineKeyboardButton("MasterCard", callback_data="mastercard")
    amex_button = types.InlineKeyboardButton("Amex", callback_data="amex")
    discover_button = types.InlineKeyboardButton("Discover", callback_data="discover")
    jcb_button = types.InlineKeyboardButton("JCB", callback_data="jcb")
    diners_button = types.InlineKeyboardButton("Diners Club", callback_data="diners")
    maestro_button = types.InlineKeyboardButton("Maestro", callback_data="maestro")
    random_button = types.InlineKeyboardButton("Rastgele", callback_data="rastgele")
    markup.add(visa_button, mastercard_button, amex_button, discover_button, jcb_button, diners_button, maestro_button, random_button)
    bot.send_message(call.message.chat.id, "Hangi kart türünü istersin?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["visa", "mastercard", "amex", "discover", "jcb", "diners", "maestro", "rastgele"])
def handle_bin_selection(call):
    if call.data == "visa":
        bin_number = "4"
    elif call.data == "mastercard":
        bin_number = "5"
    elif call.data == "amex":
        bin_number = "37"
    elif call.data == "discover":
        bin_number = "6"
    elif call.data == "jcb":
        bin_number = "35"
    elif call.data == "diners":
        bin_number = "36"
    elif call.data == "maestro":
        bin_number = "5018"
    elif call.data == "rastgele":
        bin_number = None

    bot.send_message(call.message.chat.id, "Kaç kart oluşturulsun?")
    bot.register_next_step_handler(call.message, lambda msg: generate_selected_cards(msg, bin_number))

def generate_selected_cards(message, bin_number):
    try:
        count = int(message.text)
        cards = generate_credit_cards(count, bin_number=bin_number)
        with open("H#shtaginc seçili kartlar.txt", "w") as f:
            f.write("\n".join(cards))
        with open("H#shtaginc seçili kartlar.txt", "rb") as f:
            bot.send_document(message.chat.id, f)
    except ValueError:
        bot.send_message(message.chat.id, "Geçersiz sayı girişi!")

@bot.callback_query_handler(func=lambda call: call.data == "cc_checker")
def cc_checker(call):
    markup = types.ForceReply(selective=False)
    bot.send_message(call.message.chat.id, "Lütfen combo dosyasını TXT olarak gönderin veya direkt olarak metin olarak yapıştırın.", reply_markup=markup)
    bot.send_message(call.message.chat.id, "Lütfen bekleyiniz... Kartlarınız doğrulanıyor.")
    bot.register_next_step_handler(call.message, handle_cc_check)

def handle_cc_check(message):
    if message.document:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            combo_content = downloaded_file.decode('utf-8').splitlines()
            check_cc_list(message.chat.id, combo_content)
        except Exception as e:
            bot.send_message(message.chat.id, f"Dosya işlenirken hata oluştu: {e}")
    else:
        combo_content = message.text.splitlines()
        check_cc_list(message.chat.id, combo_content)

def check_cc_list(chat_id, combo_content):
    headers = {
        'authority': 'www.xchecker.cc',
        'accept': '*/*',
        'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.xchecker.cc',
        'referer': 'https://www.xchecker.cc/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    live_count = 0
    declined_count = 0
    results = []

    bot.send_message(chat_id, "Lütfen bekleyiniz... Kartlarınız doğrulanıyor.")

    for kart in combo_content:
        kart = kart.strip()
        if not kart: continue
        url = f"https://www.xchecker.cc/api.php?cc={kart}"
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                if "live" in r.text.lower():
                    results.append(f"► {kart} | ✅")
                    live_count += 1
                else:
                    results.append(f"░ {kart} | ⛔")
                    declined_count += 1
            else:
                results.append(f"☠ {kart} | ☠")
        except requests.exceptions.RequestException as e:
            results.append(f"❗ {kart} | Error: {e}")
            time.sleep(1)

    output = "░▒▓█ ＣＣ ＣＨＥＣＫ ＲＥＳＵＬＴＳ █▓▒░\n\n"
    output += "ＬＩＶＥ ＣＡＲＤＳ:\n"
    output += "\n".join([res for res in results if "✅" in res]) + "\n\n"
    output += "ＤＥＣＬＩＮＥＤ ＣＡＲＤＳ:\n"
    output += "\n".join([res for res in results if "⛔" in res]) + "\n\n"
    output += "ＥＲＲＯＲ ＣＡＲＤＳ:\n"
    output += "\n".join([res for res in results if "☠" in res]) + "\n"

    with open("H#shtaginc cc check.txt", "w", encoding="utf-8") as f:
        f.write(output)
    with open("H#shtaginc cc check.txt", "rb") as f:
        bot.send_document(chat_id, f)
    bot.send_message(chat_id, f"✅ Live: {live_count}\n⛔ Declined: {declined_count}")

bot.infinity_polling()

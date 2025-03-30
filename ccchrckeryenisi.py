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

def generate_credit_cards(count, bin_number=None, length=None, bank=None, city=None, card_types=None):
    cards = []
    available_bins = ['4', '5', '6', '37', '6', '35', '36', '5018']
    if card_types:
        bins = [
            '4' if 'Visa' in card_types else None,
            '5' if 'MasterCard' in card_types else None,
            '37' if 'Amex' in card_types else None,
            '6' if 'Discover' in card_types else None,
            '35' if 'JCB' in card_types else None,
            '36' if 'Diners Club' in card_types else None,
            '5018' if 'Maestro' in card_types else None
        ]
        bins = [b for b in bins if b]  # None olanları temizle
    for _ in range(count):
        if not bin_number:
            if card_types:
                bin_number = random.choice(bins)
            else:
                bin_number = random.choice(available_bins)
        if not length:
            length = random.choice([15, 16])
        card_number = generate_credit_card(bin_number, length)
        cvv = ''.join(random.choice('0123456789') for _ in range(3))
        expiry_month = str(random.randint(1, 12)).zfill(2)
        expiry_year = str(random.randint(24, 29))
        card_info = f"{card_number}|{expiry_month}|{expiry_year}|{cvv}"
        if bank:
            card_info += f"|{bank}"
        if city:
            card_info += f"|{city}"
        cards.append(card_info)
    return cards

def is_valid_iban(iban):
    iban = iban.upper().replace(' ', '')
    if len(iban) < 15 or len(iban) > 34 or not iban.isalnum():
        return False
    iban_rearranged = iban[4:] + iban[:4]
    iban_int = ''
    for char in iban_rearranged:
        if char.isdigit():
            iban_int += char
        else:
            iban_int += str(ord(char) - 55)
    return int(iban_int) % 97 == 1

def generate_random_iban(country_code, bank_code=None):
    iban = country_code.upper()
    if bank_code:
        iban += bank_code.upper()
    else:
        iban += ''.join(random.choice('0123456789') for _ in range(4))  # Rastgele banka kodu (varsa daha uzun)
    account_number = ''.join(random.choice('0123456789') for _ in range(16))  # Rastgele hesap numarası (varsa daha uzun)
    iban += account_number
    iban_rearranged = iban[4:] + iban[:4]
    iban_int = ''
    for char in iban_rearranged:
        if char.isdigit():
            iban_int += char
        else:
            iban_int += str(ord(char) - 55)
    check_digits = str(98 - (int(iban_int) % 97)).zfill(2)  # Kontrol rakamları
    return iban[:2] + check_digits + iban[2:]  # IBAN'ı oluştur

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    cc_olustur_button = types.InlineKeyboardButton("Credit Card Oluştur", callback_data="cc_olustur")
    karisik_olustur_button = types.InlineKeyboardButton("Karışık Mod CC Oluştur", callback_data="karisik_olustur")
    cc_cesitlilik_button = types.InlineKeyboardButton("Kart Çeşitliliği Oluştur", callback_data="cc_cesitlilik")
    iban_sorgu_button = types.InlineKeyboardButton("IBAN Sorgula", callback_data="iban_sorgu")
    iban_uret_button = types.InlineKeyboardButton("Rastgele IBAN Üret", callback_data="iban_uret")  # Yeni eklenen buton
    cc_checker_button = types.InlineKeyboardButton("CC Checker", callback_data="cc_checker")
    markup.add(cc_olustur_button, karisik_olustur_button, cc_cesitlilik_button, iban_sorgu_button, iban_uret_button, cc_checker_button)  # Yeni buton eklendi
    bot.send_message(message.chat.id, "Selam! Ne istersin? 😈", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "cc_olustur")
def cc_olustur(call):
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
    bot.register_next_step_handler(call.message, handle_firm_selection)

firm_data = {}

def handle_firm_selection(message):
    firm_data[message.chat.id] = {"firm": message.text}
    markup = types.InlineKeyboardMarkup(row_width=1)
    bank_options = ["Garanti", "Akbank", "Yapı Kredi", "İş Bankası"]
    for bank in bank_options:
        markup.add(types.InlineKeyboardButton(bank, callback_data=f"bank_{bank}"))
    bot.send_message(message.chat.id, "Hangi bankayı istersin?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("bank_"))
def handle_bank_selection(call):
    selected_bank = call.data.split("bank_")[1]
    firm_data[call.message.chat.id]["bank"] = selected_bank
    bot.send_message(call.message.chat.id, "Hangi şehri istersin?")
    bot.register_next_step_handler(call.message, handle_city_selection)

def handle_city_selection(message):
    firm_data[message.chat.id]["city"] = message.text
    bot.send_message(message.chat.id, "Kaç kart oluşturulsun?")
    bot.register_next_step_handler(message, generate_selected_cards)

def generate_selected_cards(message):
    try:
        count = int(message.text)
        data = firm_data.pop(message.chat.id)
        cards = generate_credit_cards(count, bin_number=data.get("firm"), bank=data.get("bank"), city=data.get("city"))
        with open("H#shtaginc seçili kartlar.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(cards))
        with open("H#shtaginc seçili kartlar.txt", "rb") as f:
            bot.send_document(message.chat.id, f)
    except ValueError:
        bot.send_message(message.chat.id, "Geçersiz sayı girişi!")

@bot.callback_query_handler(func=lambda call: call.data == "karisik_olustur")
def karisik_olustur(call):
    bot.send_message(call.message.chat.id, "Kaç adet kart oluşturulacak?")
    bot.register_next_step_handler(call.message, generate_random_cards_handler)

def generate_random_cards_handler(message):
    try:
        count = int(message.text)
        cards = generate_credit_cards(count)
        with open("H#shtaginc karışık kartlar.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(cards))
        with open("H#shtaginc karışık kartlar.txt", "rb") as f:
            bot.send_document(message.chat.id, f)
    except ValueError:
        bot.send_message(message.chat.id, "Geçersiz sayı girişi!")

@bot.callback_query_handler(func=lambda call: call.data == "cc_cesitlilik")
def cc_cesitlilik(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    visa_button = types.InlineKeyboardButton("Visa", callback_data="cc_cesitlilik_visa")
    mastercard_button = types.InlineKeyboardButton("MasterCard", callback_data="cc_cesitlilik_mastercard")
    amex_button = types.InlineKeyboardButton("Amex", callback_data="cc_cesitlilik_amex")
    discover_button = types.InlineKeyboardButton("Discover", callback_data="cc_cesitlilik_discover")
    jcb_button = types.InlineKeyboardButton("JCB", callback_data="cc_cesitlilik_jcb")
    diners_button = types.InlineKeyboardButton("Diners Club", callback_data="cc_cesitlilik_diners")
    maestro_button = types.InlineKeyboardButton("Maestro", callback_data="cc_cesitlilik_maestro")
    all_button = types.InlineKeyboardButton("Tümünü Seç", callback_data="cc_cesitlilik_all")
    markup.add(visa_button, mastercard_button, amex_button, discover_button, jcb_button, diners_button, maestro_button, all_button)
    bot.send_message(call.message.chat.id, "Hangi kart türlerini istiyorsun? (En az birini seçin)", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cc_cesitlilik_"))
def handle_cc_cesitlilik_selection(call):
    selected_types = []
    if call.data == "cc_cesitlilik_visa":
        selected_types.append("Visa")
    elif call.data == "cc_cesitlilik_mastercard":
        selected_types.append("MasterCard")
    elif call.data == "cc_cesitlilik_amex":
        selected_types.append("Amex")
    elif call.data == "cc_cesitlilik_discover":
        selected_types.append("Discover")
    elif call.data == "cc_cesitlilik_jcb":
        selected_types.append("JCB")
    elif call.data == "cc_cesitlilik_diners":
        selected_types.append("Diners Club")
    elif call.data == "cc_cesitlilik_maestro":
        selected_types.append("Maestro")
    elif call.data == "cc_cesitlilik_all":
        selected_types = ["Visa", "MasterCard", "Amex", "Discover", "JCB", "Diners Club", "Maestro"]
    bot.send_message(call.message.chat.id, "Kaç kart oluşturulsun?")
    bot.register_next_step_handler(call.message, lambda msg: generate_cc_cesitlilik_cards(msg, selected_types))

def generate_cc_cesitlilik_cards(message, card_types):
    try:
        count = int(message.text)
        cards = generate_credit_cards(count, card_types=card_types)
        with open("H#shtaginc çeşitli kartlar.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(cards))
        with open("H#shtaginc çeşitli kartlar.txt", "rb") as f:
            bot.send_document(message.chat.id, f)
    except ValueError:
        bot.send_message(message.chat.id, "Geçersiz sayı girişi!")

@bot.callback_query_handler(func=lambda call: call.data == "iban_sorgu")
def iban_sorgu(call):
    bot.send_message(call.message.chat.id, "Lütfen IBAN'ı girin:")
    bot.register_next_step_handler(call.message, handle_iban_check)

def handle_iban_check(message):
    iban = message.text
    if is_valid_iban(iban):
        bot.send_message(message.chat.id, f"✅ {iban} geçerli bir IBAN'dır.")
        # Daha detaylı sorgulama için (API veya veri tabanı) burada geliştirmeler yapabilirsiniz.
    else:
        bot.send_message(message.chat.id, f"⛔ {iban} geçerli bir IBAN değildir.")

@bot.callback_query_handler(func=lambda call: call.data == "iban_uret")  # Yeni fonksiyon
def iban_uret(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    tr_button = types.InlineKeyboardButton("Türkiye", callback_data="iban_uret_tr")
    de_button = types.InlineKeyboardButton("Almanya", callback_data="iban_uret_de")
    # ... (Diğer ülkeler eklenebilir)
    random_button = types.InlineKeyboardButton("Rastgele Ülke", callback_data="iban_uret_random")
    markup.add(tr_button, de_button, random_button)
    bot.send_message(call.message.chat.id, "Hangi ülke için IBAN oluşturulsun?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("iban_uret_"))  # Yeni fonksiyon
def handle_iban_uret_selection(call):
    country_code = None
    if call.data == "iban_uret_tr":
        country_code = "TR"
    elif call.data == "iban_uret_de":
        country_code = "DE"
    elif call.data == "iban_uret_random":
        country_code = random.choice(["TR", "DE", "FR", "NL"])  # Daha fazla ülke eklenebilir

    iban = generate_random_iban(country_code)
    bot.send_message(call.message.chat.id, f"🎉 Rastgele IBAN: {iban}")

@bot.callback_query_handler(func=lambda call: call.data == "cc_checker")
def cc_checker(call):
    markup = types.ForceReply(selective=False)
    bot.send_message(call.message.chat.id, "Lütfen combo dosyasını TXT olarak gönderin veya direkt olarak metin olarak yapıştırın.", reply_markup=markup)
    bot.register_next_step_handler(call.message, handle_cc_check)

def handle_cc_check(message):
    bot.send_message(message.chat.id, "Lütfen bekleyiniz... Kartlarınız doğrulanıyor.")
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

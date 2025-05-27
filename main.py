import telebot
import re

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(API_TOKEN)

# ON/OFF fitur auto delete pesan forward / link
AUTO_DELETE_FORWARD = True


# ---------- Fitur 1: Rekap Data ----------

def parse_rekap(text):
    lines = text.strip().splitlines()
    k_numbers = []
    b_numbers = []
    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.upper().startswith('K'):
            current_section = 'K'
            continue
        elif line.upper().startswith('B'):
            current_section = 'B'
            continue

        if current_section in ['K', 'B']:
            nums = re.findall(r'\d+', line)
            if nums:
                num = int(nums[0])
                if current_section == 'K':
                    k_numbers.append(num)
                else:
                    b_numbers.append(num)

    total_k = sum(k_numbers)
    total_b = sum(b_numbers)
    saldo = total_k + total_b

    k_str = ", ".join(str(n) for n in k_numbers)
    b_str = ", ".join(str(n) for n in b_numbers)

    if total_k == total_b:
        status = "K dan B sudah seimbang!"
    elif total_k > total_b:
        kurang = total_k - total_b
        status = f"B masih kurang [ -{kurang} K ]"
    else:
        kurang = total_b - total_k
        status = f"K masih kurang [ -{kurang} K ]"

    saldo_ribuan = f"{saldo}K"

    result = (
        f"K: [{k_str}] = {total_k}\n\n"
        f"B: [{b_str}] = {total_b}\n\n"
        f"{status}\n\n"
        f"Saldo Anda: {saldo_ribuan}"
    )

    return result


# ---------- Fitur 2: Rekap Win ----------

def fee_reduce(num):
    # fee sesuai rentang angka
    if 1 <= num <= 9:
        return 1
    elif 10 <= num <= 20:
        return 2
    elif 21 <= num <= 30:
        return 3
    elif 31 <= num <= 40:
        return 4
    elif 41 <= num <= 50:
        return 5
    elif 51 <= num <= 60:
        return 6
    elif 61 <= num <= 70:
        return 7
    elif 71 <= num <= 80:
        return 8
    elif 81 <= num <= 90:
        return 9
    elif 91 <= num <= 100:
        return 10
    else:
        return 10 + (num - 100) // 10

def parse_rekap_win(text):
    lines = text.strip().splitlines()
    current_section = None

    result_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            result_lines.append("")
            continue

        if line.upper().startswith('K'):
            current_section = 'K'
            result_lines.append("K :")
            continue
        elif line.upper().startswith('B'):
            current_section = 'B'
            result_lines.append("B :")
            continue

        if current_section in ['K', 'B']:
            nums = re.findall(r'\d+', line)
            if nums:
                num = int(nums[0])
                fee = fee_reduce(num)
                hasil = num - fee
                name_match = re.match(r"(\S+)", line)
                name = name_match.group(1) if name_match else ""
                result_lines.append(f"{name} {num} // +{hasil}")
            else:
                result_lines.append(line)
        else:
            result_lines.append(line)

    return "\n".join(result_lines)


# ---------- Fitur 3: Auto Delete Forward dan Link Telegram ----------

def contains_telegram_link(message):
    if not message.text:
        return False

    if message.entities:
        for entity in message.entities:
            if entity.type == 'url':
                url_text = message.text[entity.offset:entity.offset + entity.length].lower()
                if 't.me' in url_text:
                    return True
            elif entity.type == 'text_link':
                if entity.url and 't.me' in entity.url.lower():
                    return True

    if 't.me' in message.text.lower():
        return True

    return False

def contains_telegram_link_in_caption(message):
    if not message.caption:
        return False

    if message.caption_entities:
        for entity in message.caption_entities:
            if entity.type == 'url':
                url_text = message.caption[entity.offset:entity.offset + entity.length].lower()
                if 't.me' in url_text:
                    return True
            elif entity.type == 'text_link':
                if entity.url and 't.me' in entity.url.lower():
                    return True

    if 't.me' in message.caption.lower():
        return True

    return False


@bot.message_handler(commands=['rekap'])
def handle_rekap(message):
    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption or ""
        hasil = parse_rekap(text)
        bot.reply_to(message, hasil)
    else:
        bot.reply_to(message, "Mohon reply ke pesan yang berisi data untuk direkap.")


@bot.message_handler(commands=['rekapwin'])
def handle_rekap_win(message):
    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption or ""
        hasil = parse_rekap_win(text)
        bot.reply_to(message, hasil)
    else:
        bot.reply_to(message, "Mohon reply ke pesan yang berisi data untuk direkap win.")


@bot.message_handler(func=lambda m: AUTO_DELETE_FORWARD and (
    m.forward_date is not None or 
    contains_telegram_link(m) or 
    contains_telegram_link_in_caption(m)
))
def delete_forward_or_link_message(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(f"Gagal hapus pesan: {e}")


print("Bot running... Made With Love by RzkyO")
bot.infinity_polling()

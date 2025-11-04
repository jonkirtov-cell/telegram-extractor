# 📦 Установи зависимости
!pip install telethon tqdm

# 🧠 Импорт
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.sessions import StringSession
from tqdm import tqdm
import csv
import asyncio

# 🔐 Данные Telegram API
api_id = 27021422
api_hash = 'bc04608f4880baae617c9ac32751a7f4'
phone = '+37257375523'

client = TelegramClient(StringSession(), api_id, api_hash)

# 📋 Основная функция
async def main():
    try:
        await client.start(phone=phone)
        chat_name = input("Введите username или ID чата: ")
        chat = await client.get_entity(chat_name)

        print("📥 Получаем участников...")
        participants = []
        offset = 0
        limit = 100

        while True:
            part = await client(GetParticipantsRequest(
                chat, ChannelParticipantsSearch(''), offset, limit, hash=0
            ))
            if not part.users:
                break
            participants.extend(part.users)
            offset += len(part.users)
            await asyncio.sleep(1)  # 🛡️ Защита от бана

        print(f"✅ Получено участников: {len(participants)}")

        # 💾 Сохраняем участников
        with open("user_chat.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["user_id", "username", "name", "bio"])
            for user in participants:
                username = user.username or ""
                name = (user.first_name or "") + " " + (user.last_name or "")
                bio = getattr(user, "about", "")
                writer.writerow([user.id, username, name.strip(), bio])

        print("📥 Получаем последние 1500 сообщений...")
        messages = await client.get_messages(chat, limit=1500)
        print(f"✅ Получено сообщений: {len(messages)}")

        # 💾 Сохраняем сообщения
        with open("messag.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["msg_id", "user_id", "username", "text"])
            for msg in messages:
                sender = await msg.get_sender()
                uid = sender.id if sender else ""
                uname = sender.username if sender and sender.username else ""
                text = msg.message.replace("\n", " ") if msg.message else ""
                writer.writerow([msg.id, uid, uname, text])

        # 🔍 Сравниваем активность
        print("🔍 Анализируем неактивных участников...")
        active_ids = set()
        for msg in messages:
            sender = await msg.get_sender()
            if sender:
                active_ids.add(sender.id)

        with open("result.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["user", "описание профиля / сообщения"])

            for user in tqdm(participants, desc="📊 Сравнение"):
                if user.id not in active_ids:
                    bio = getattr(user, "about", "")
                    writer.writerow([user.username or user.id, bio])

        print("✅ Готово! Файл result.csv содержит неактивных участников.")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

# 🚀 Запуск
await main()

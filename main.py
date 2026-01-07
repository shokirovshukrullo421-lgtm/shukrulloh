import os
import asyncio
from telethon import TelegramClient, events

# ================== SOZLAMALAR ==================

api_id = 12345678          # <-- O'ZINGNIKI
api_hash = "API_HASH_BU_YERGA"  # <-- O'ZINGNIKI

BOT_USERNAME = "kuy_navo_bot"   # bot username (@siz)
LINKS_FILE = "links.txt"
DOWNLOAD_DIR = "videos"

# ================================================

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

client = TelegramClient("session", api_id, api_hash)

async def main():
    # linklarni o‘qish
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        links = [l.strip() for l in f if l.strip()]

    print(f"🔗 Jami linklar: {len(links)}")

    for idx, link in enumerate(links, start=1):
        print(f"\n[{idx}/{len(links)}] Botga yuborildi: {link}")

        await client.send_message(BOT_USERNAME, link)

        print("⏳ Video kutilmoqda...")

        # video kelguncha kutish
        async for message in client.iter_messages(BOT_USERNAME, limit=5):
            if message.video:
                file_path = await message.download_media(file=DOWNLOAD_DIR)
                print(f"✅ Video saqlandi: {file_path}")
                break

        await asyncio.sleep(5)  # botni charchatmaslik uchun

    print("\n🎉 BARCHA LINKLAR TUGADI!")

# ishga tushirish
with client:
    client.loop.run_until_complete(main())

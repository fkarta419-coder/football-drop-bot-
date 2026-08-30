import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT = Bot(token=TOKEN)
DP = Dispatcher()

@DP.message(Command("start"))
async def start(message: Message):
    await message.answer("✅ ИИ-БОТ РАБОТАЕТ!\n\nТеперь вставляй полный код!")

@DP.message()
async def echo(message: Message):
    await message.answer(f"Ты написал: {message.text}")

async def main():
    await DP.start_polling(BOT)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

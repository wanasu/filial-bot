import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatPermissions
from aiogram.utils import executor

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Пример: @filialmsk

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Проверка подписки
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# Когда новый участник заходит
@dp.chat_member_handler()
async def handle_new_member(update: types.ChatMemberUpdated):
    if update.new_chat_member.status == 'member':
        user_id = update.from_user.id
        chat_id = update.chat.id
        if not await is_subscribed(user_id):
            # Мутим пользователя
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            # Отправляем сообщение
            await bot.send_message(
                chat_id=chat_id,
                text=f"{update.from_user.full_name}, подпишись на {CHANNEL_ID}, чтобы писать!",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("Подписаться", url=f"https://t.me/{CHANNEL_ID[1:]}")
                )
            )

# Команда /unmute для разблокировки после подписки
@dp.message_handler(commands=['unmute'])
async def unmute_user(message: types.Message):
    if await is_subscribed(message.from_user.id):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            permissions=ChatPermissions(can_send_messages=True)
        )
        await message.reply("Ты подписан — теперь можешь писать!")
    else:
        await message.reply("Сначала подпишись на канал!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

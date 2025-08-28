from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN
from handlers import manager, admin

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Utility: return user ID
async def my_id(message: types.Message):
    await message.answer(f"Sizning ID: {message.from_user.id}")

# Handlers
dp.register_message_handler(my_id, commands=["myid"])
manager.register_manager_handlers(dp)
admin.register_admin_handlers(dp)

# Scheduler background task
import asyncio
from scheduler import monitor_issues, weekly_report_scheduler

async def on_startup(dp):
    asyncio.create_task(monitor_issues())
    asyncio.create_task(weekly_report_scheduler())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

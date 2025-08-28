from report_utils import send_weekly_report
async def weekly_report_scheduler():
    while True:
        now = time.localtime()
        # Har dushanba soat 09:00 da yuboriladi
        if now.tm_wday == 0 and now.tm_hour == 9 and now.tm_min < 10:
            await send_weekly_report()
            await asyncio.sleep(600)  # 10 daqiqa kutish, takrorlanmasligi uchun
        await asyncio.sleep(300)  # 5 daqiqada bir tekshiradi
import asyncio
import time
from aiogram import Bot
from database import load_data, save_data
from config import TOKEN, MANAGER_IDS

bot = Bot(token=TOKEN)

async def monitor_issues():
    while True:
        data = load_data()
        now = int(time.time())
        changed = False
        for issue in data.get('issues', []):
            # 12 soat: menejerdan so‘rash
            if issue['status'] == 'open' and now - issue['timestamp'] > 12*3600 and not issue.get('asked_manager'):
                await bot.send_message(issue['manager_id'], f"Admin (ID: {issue['admin_id']}) uchun muammo hal bo‘lmadi. Muammo: {issue['text']}\nHal bo‘ldimi? /hal_boldi_{issue['timestamp']} yoki /rad_{issue['timestamp']}")
                issue['asked_manager'] = True
                changed = True
            # 24 soat: barcha menejerlarga eskalatsiya
            if issue['status'] == 'open' and now - issue['timestamp'] > 24*3600 and not issue.get('escalated'):
                for manager_id in MANAGER_IDS:
                    await bot.send_message(manager_id, f"Eskalatsiya: Admin (ID: {issue['admin_id']}) uchun muammo 24 soatdan beri hal qilinmadi!\nMuammo: {issue['text']}")
                issue['escalated'] = True
                changed = True
        if changed:
            save_data(data)
        await asyncio.sleep(600)  # 10 daqiqada bir tekshiradi

# Bu funksiyani main.py da background task sifatida ishga tushirish kerak

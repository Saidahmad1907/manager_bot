import time
from aiogram import Bot
from database import load_data
from config import TOKEN, MANAGER_IDS, ADMIN_IDS

bot = Bot(token=TOKEN)

def get_weekly_stats():
    data = load_data()
    now = int(time.time())
    week_ago = now - 7*24*3600
    stats = {}
    for admin_id in data.get('admins', []):
        issues = [i for i in data.get('issues', []) if i['admin_id'] == admin_id and i['timestamp'] >= week_ago]
        penalties = [p for p in data.get('penalties', []) if p['admin_id'] == admin_id and p['timestamp'] >= week_ago]
        stats[admin_id] = {
            'issues': len(issues),
            'penalties': len(penalties)
        }
    return stats

async def send_weekly_report():
    stats = get_weekly_stats()
    for admin_id, s in stats.items():
        text = f"<b>Haftalik hisobot:</b>\nYangi muammolar: {s['issues']}\nYangi jarimalar: {s['penalties']}"
        try:
            await bot.send_message(admin_id, text, parse_mode="HTML")
        except Exception:
            pass
    for manager_id in MANAGER_IDS:
        text = "<b>Barcha adminlar uchun haftalik hisobot:</b>\n"
        for admin_id, s in stats.items():
            text += f"Admin {admin_id}: Muammolar: {s['issues']}, Jarimalar: {s['penalties']}\n"
        try:
            await bot.send_message(manager_id, text, parse_mode="HTML")
        except Exception:
            pass

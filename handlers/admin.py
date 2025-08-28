from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import MANAGER_IDS
from database import (
    load_data,
    save_data,
    verify_admin_credentials,
    start_session,
    get_session_admin_id,
    end_session,
)
import time


async def _require_session(message: types.Message):
    admin_id = get_session_admin_id(message.from_user.id)
    if not admin_id:
        await message.answer("Avval tizimga kiring: /login <login> <parol>")
        return None
    # blocked check on every action
    data = load_data()
    if admin_id in data.get('blocked_admins', []):
        await message.answer("Hisobingiz bloklangan. Menejer bilan bog'laning.")
        return None
    return admin_id


async def login_cmd(message: types.Message):
    args = message.get_args().split()
    if len(args) < 2:
        await message.answer("Foydalanish: /login <login> <parol>")
        return
    login, password = args[0], args[1]
    admin_id = verify_admin_credentials(login, password)
    if not admin_id:
        await message.answer("Login yoki parol noto'g'ri.")
        return
    # Credential belongs to specific admin_id; only that Telegram user can use it
    if admin_id != message.from_user.id:
        await message.answer("Bu login/parol boshqa admin uchun mo'ljallangan.")
        return
    data = load_data()
    if admin_id in data.get('blocked_admins', []):
        await message.answer("Siz bloklangansiz. Kirish rad etildi.")
        return
    start_session(message.from_user.id, admin_id, int(time.time()))
    await message.answer("Muvaffaqiyatli kirdingiz. /admin orqali panelni oching.")


async def logout_cmd(message: types.Message):
    end_session(message.from_user.id)
    await message.answer("Hisobdan chiqildi.")

async def my_profile(message: types.Message):
    admin_id = await _require_session(message)
    if not admin_id:
        return
    data = load_data()
    issues = [i for i in data.get('issues', []) if i['admin_id'] == admin_id]
    resolved = [i for i in issues if i['status'] in ('resolved', 'resolved_by_manager')]
    penalties = [p for p in data.get('penalties', []) if p['admin_id'] == admin_id]
    warnings = [w for w in data.get('warnings', []) if w['admin_id'] == admin_id] if 'warnings' in data else []
    blocked = admin_id in data.get('blocked_admins', [])
    text = f"<b>Profil:</b>\nID: {admin_id}\nHal qilingan muammolar: {len(resolved)}\nJarimalar: {len(penalties)}\nOgohlantirishlar: {len(warnings)}\nHolat: {'Bloklangan' if blocked else 'Faol'}"
    await message.answer(text, parse_mode="HTML")
async def my_history(message: types.Message):
    admin_id = await _require_session(message)
    if not admin_id:
        return
    data = load_data()
    # Muammolar
    issues = [i for i in data.get('issues', []) if i['admin_id'] == admin_id]
    # Jarimalar
    penalties = [p for p in data.get('penalties', []) if p['admin_id'] == admin_id]
    text = f"<b>Muammolar:</b>\n"
    for i in issues:
        text += f"- {i['text']} | Holat: {i['status']} | {time.strftime('%Y-%m-%d %H:%M', time.localtime(i['timestamp']))}\n"
    text += f"\n<b>Jarimalar:</b>\n"
    for p in penalties:
        text += f"- {p['reason']} | {time.strftime('%Y-%m-%d %H:%M', time.localtime(p['timestamp']))}\n"
    await message.answer(text or "Tarix topilmadi.", parse_mode="HTML")
async def statistics(message: types.Message):
    admin_id = await _require_session(message)
    if not admin_id:
        return
    data = load_data()
    admin_count = len(data.get('admins', []))
    manager_count = len(data.get('managers', []))
    complaints = len(data.get('complaints', []))
    penalties = len(data.get('penalties', []))
    issues = len(data.get('issues', [])) if 'issues' in data else 0
    await message.answer(f"<b>Statistika:</b>\nAdminlar: {admin_count}\nMenejerlar: {manager_count}\nShikoyatlar: {complaints}\nJarimalar: {penalties}\nMuammolar: {issues}", parse_mode="HTML")
 


async def admin_panel(message: types.Message):
    admin_id = get_session_admin_id(message.from_user.id)
    if admin_id:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("Mening shikoyatlarim"), KeyboardButton("Mening jarimalarim"))
    kb.row(KeyboardButton("Shikoyatni hal qilish"), KeyboardButton("Jarimani to'lash"))
    kb.row(KeyboardButton("Mening statistikam"), KeyboardButton("Yangilash"))
    kb.row(KeyboardButton("Yordam"))
    await message.answer("Admin paneliga xush kelibsiz! Quyidagi tugmalardan foydalaning.", reply_markup=kb)
    else:
        await message.answer("Avval tizimga kiring: /login <login> <parol>")

# Admin o‘ziga biriktirilgan ochiq shikoyatlarni ko‘radi
async def my_complaints(message: types.Message):
    admin_id = await _require_session(message)
    if not admin_id:
        return
    data = load_data()
    comps = [c for c in data.get('complaints', []) if c.get('admin_id') == admin_id and c.get('status') == 'open']
    if not comps:
        await message.answer("Sizga biriktirilgan ochiq shikoyatlar yo‘q.")
        return
    for c in comps:
        await message.answer(f"Shikoyat: {c['text']}\nID: {c['timestamp']}\n/javob {c['timestamp']} <matn>")

# /javob <complaint_id> <matn> — admin menejerga bot orqali javob yuboradi
async def reply_complaint(message: types.Message):
    admin_id = await _require_session(message)
    if not admin_id:
        return
    args = message.get_args().split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Foydalanish: /javob <complaint_id> <matn>")
        return
    comp_id_s, reply_text = args
    data = load_data()
    for c in data.get('complaints', []):
        if str(c['timestamp']) == comp_id_s and c['admin_id'] == admin_id and c.get('status') == 'open':
            c['responses'].append({'from': 'admin', 'text': reply_text, 'timestamp': int(time.time())})
            save_data(data)
            await message.answer("Javob yuborildi.")
            # Menejerga xabar yuborish
            try:
                await message.bot.send_message(c['manager_id'], f"Admin {message.from_user.id} javobi (shikoyat {comp_id_s}): {reply_text}")
            except Exception:
                pass
            return
    await message.answer("Shikoyat topilmadi yoki yopilgan.")

# /muammolarim - admin o‘ziga biriktirilgan ochiq muammolarni ko‘radi va hal qilishi mumkin
async def my_issues(message: types.Message):
    admin_id = await _require_session(message)
    if not admin_id:
        return
    data = load_data()
    issues = [i for i in data.get('issues', []) if i['admin_id'] == admin_id and i['status'] == 'open']
    if not issues:
        await message.answer("Sizga biriktirilgan ochiq muammolar yo‘q.")
        return
    for idx, issue in enumerate(issues, 1):
        await message.answer(f"#{idx}\nMuammo: {issue['text']}\nYuborilgan: <code>{time.strftime('%Y-%m-%d %H:%M', time.localtime(issue['timestamp']))}</code>\n/muammo_hal {issue['timestamp']}")

# /muammo_hal <timestamp> - admin muammoni hal qilganini bildiradi
async def resolve_issue(message: types.Message):
    admin_id = await _require_session(message)
    if not admin_id:
        return
    args = message.get_args().strip()
    if not args:
        await message.answer("Foydalanish: /muammo_hal <timestamp>")
        return
    data = load_data()
    for issue in data.get('issues', []):
        if issue['admin_id'] == admin_id and str(issue['timestamp']) == args and issue['status'] == 'open':
            issue['status'] = 'resolved'
            save_data(data)
            await message.answer("Muammo hal qilindi va yopildi.")
            return
    await message.answer("Bunday ochiq muammo topilmadi.")


# --------- Qo'shimcha label tugmalar uchun handlerlar ---------

async def admin_help(message: types.Message):
    admin_id = await _require_session(message)
    if not admin_id:
        return
    text = (
        "Yordam:\n"
        "- Mening shikoyatlarim: Sizga biriktirilgan ochiq shikoyatlar ro'yxati.\n"
        "- Mening jarimalarim: Sizga yozilgan jarimalar.\n"
        "- Shikoyatni hal qilish: Sizga biriktirilgan ochiq muammolarni ko'rish va hal qilish.\n"
        "- Jarimani to'lash: Jarima uchun to'langanligini belgilash.\n"
        "- Mening statistikam: Umumiy statistika.\n"
        "- Yangilash: Panelni qayta yuklash.\n"
        "Qo'shimcha buyruqlar: /javob <id> <matn>, /muammo_hal <id>, /logout"
    )
    await message.answer(text)


async def admin_refresh(message: types.Message):
    await admin_panel(message)


async def my_penalties(message: types.Message):
    admin_id = await _require_session(message)
    if not admin_id:
        return
    data = load_data()
    pens = [p for p in data.get('penalties', []) if p['admin_id'] == admin_id]
    if not pens:
        await message.answer("Sizga jarima yozilmagan.")
        return
    text = "<b>Mening jarimalarim:</b>\n"
    for p in pens:
        paid = p.get('paid')
        status = "to'langan" if paid else "to'lanmagan"
        text += f"- ID: {p['timestamp']} | {p['reason']} | Holat: {status} | {time.strftime('%Y-%m-%d %H:%M', time.localtime(p['timestamp']))}\n"
    text += "\nTo'lovni belgilash: To'landi <ID> yoki /tolandi <ID>"
    await message.answer(text, parse_mode="HTML")


async def pay_penalty_text(message: types.Message):
    # Accept formats: "To'landi <id>" or "/tolandi <id>"
    admin_id = await _require_session(message)
    if not admin_id:
        return
    content = message.text.strip()
    if content.startswith("To'landi "):
        _, ts = content.split(maxsplit=1)
    elif content.startswith("/tolandi "):
        _, ts = content.split(maxsplit=1)
    else:
        return  # not our message
    data = load_data()
    for p in data.get('penalties', []):
        if str(p['timestamp']) == ts and p['admin_id'] == admin_id:
            p['paid'] = True
            p['paid_ts'] = int(time.time())
            save_data(data)
            await message.answer("Jarima to'landi deb belgilandi.")
            # Xabar menejerlarga
            for mid in data.get('managers', []) or MANAGER_IDS:
                try:
                    await message.bot.send_message(mid, f"Admin {admin_id} jarimani to'landi deb belgiladi (ID: {ts}).")
                except Exception:
                    pass
            return
    await message.answer("Jarima topilmadi.")


async def my_issues_button(message: types.Message):
    # Triggered by label "Shikoyatni hal qilish" – list issues and show instruction
    admin_id = await _require_session(message)
    if not admin_id:
        return
    await my_issues(message)
    await message.answer("Muammoni hal qilish uchun: /muammo_hal <ID>")

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(login_cmd, commands=["login"])
    dp.register_message_handler(logout_cmd, commands=["logout"])
    dp.register_message_handler(admin_panel, commands=["admin"])
    # Text buttons (Uzbek labels)
    dp.register_message_handler(my_complaints, lambda m: m.text == "Mening shikoyatlarim")
    dp.register_message_handler(my_penalties, lambda m: m.text == "Mening jarimalarim")
    dp.register_message_handler(my_issues_button, lambda m: m.text == "Shikoyatni hal qilish")
    dp.register_message_handler(pay_penalty_text, regexp=r"^(To'landi\s+\d+|/tolandi\s+\d+)$")
    dp.register_message_handler(statistics, lambda m: m.text == "Mening statistikam")
    dp.register_message_handler(admin_refresh, lambda m: m.text == "Yangilash")
    dp.register_message_handler(admin_help, lambda m: m.text == "Yordam")
    dp.register_message_handler(my_complaints, commands=["shikoyatlarim"])
    dp.register_message_handler(reply_complaint, commands=["javob"])
    dp.register_message_handler(my_issues, commands=["muammolarim"])
    dp.register_message_handler(resolve_issue, commands=["muammo_hal"])
    dp.register_message_handler(statistics, commands=["statistika"])
    dp.register_message_handler(my_history, commands=["tarix"])
    dp.register_message_handler(my_profile, commands=["profil"])

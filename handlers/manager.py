from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import MANAGER_IDS, ADMIN_IDS
from database import load_data, save_data
from database import set_admin_credentials
from utils import export_activity_csv
import time
import os
async def export_csv(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    filename = export_activity_csv()
    if os.path.exists(filename):
        await message.answer_document(open(filename, "rb"), caption="Faoliyat CSV eksporti")
        os.remove(filename)
    else:
        await message.answer("Eksportda xatolik yuz berdi.")
async def my_profile(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    data = load_data()
    issues = [i for i in data.get('issues', []) if i['manager_id'] == message.from_user.id]
    created = len(issues)
    resolved = len([i for i in issues if i['status'] in ('resolved', 'resolved_by_manager')])
    penalties = len([p for p in data.get('penalties', []) if p['manager_id'] == message.from_user.id])
    text = f"<b>Profil:</b>\nID: {message.from_user.id}\nYaratilgan muammolar: {created}\nHal qilingan muammolar: {resolved}\nYozilgan jarimalar: {penalties}"
    await message.answer(text, parse_mode="HTML")
async def manager_callback_handler(call: types.CallbackQuery):
    if call.from_user.id not in MANAGER_IDS:
        await call.answer("Ruxsat yo‘q", show_alert=True)
        return
    data = call.data
    if data == "manager_statistika":
        await statistics(call.message)
    elif data == "manager_ochiqmuammolar":
        await open_issues(call.message)
    elif data == "manager_jarimalar":
        await all_penalties(call.message)
    elif data == "manager_addadmin":
        await call.message.answer("/addadmin <user_id> komandasidan foydalaning.")
    elif data == "manager_removeadmin":
        await call.message.answer("/removeadmin <user_id> komandasidan foydalaning.")
    elif data == "manager_addmanager":
        await call.message.answer("/addmanager <user_id> komandasidan foydalaning.")
    elif data == "manager_removemanager":
        await call.message.answer("/removemanager <user_id> komandasidan foydalaning.")
    elif data == "manager_blockadmin":
        await call.message.answer("/blockadmin <user_id> komandasidan foydalaning.")
    elif data == "manager_unblockadmin":
        await call.message.answer("/unblockadmin <user_id> komandasidan foydalaning.")
    elif data == "manager_warnadmin":
        await call.message.answer("/warnadmin <user_id> <matn> komandasidan foydalaning.")
    await call.answer()
async def block_admin(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    args = message.get_args().strip()
    if not args.isdigit():
        await message.answer("Foydalanish: /blockadmin <user_id>")
        return
    user_id = int(args)
    data = load_data()
    if 'blocked_admins' not in data:
        data['blocked_admins'] = []
    if user_id in data['blocked_admins']:
        await message.answer("Bu admin allaqachon bloklangan.")
        return
    data['blocked_admins'].append(user_id)
    save_data(data)
    await message.answer(f"{user_id} vaqtincha bloklandi.")
    try:
        await message.bot.send_message(user_id, "Siz vaqtincha bloklandingiz. Iltimos, menejer bilan bog‘laning.")
    except Exception:
        pass

async def unblock_admin(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    args = message.get_args().strip()
    if not args.isdigit():
        await message.answer("Foydalanish: /unblockadmin <user_id>")
        return
    user_id = int(args)
    data = load_data()
    if 'blocked_admins' not in data or user_id not in data['blocked_admins']:
        await message.answer("Bu admin bloklangan emas.")
        return
    data['blocked_admins'].remove(user_id)
    save_data(data)
    await message.answer(f"{user_id} blokdan chiqarildi.")
    try:
        await message.bot.send_message(user_id, "Siz blokdan chiqarildingiz. Yana faoliyat yuritishingiz mumkin.")
    except Exception:
        pass

async def warn_admin(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    args = message.get_args().split(maxsplit=1)
    if len(args) < 2 or not args[0].isdigit():
        await message.answer("Foydalanish: /warnadmin <user_id> <ogohlantirish matni>")
        return
    user_id = int(args[0])
    warning_text = args[1]
    data = load_data()
    if 'warnings' not in data:
        data['warnings'] = []
    data['warnings'].append({'admin_id': user_id, 'text': warning_text, 'timestamp': int(time.time())})
    save_data(data)
    await message.answer(f"{user_id} adminiga ogohlantirish yuborildi.")
    try:
        await message.bot.send_message(user_id, f"Sizga ogohlantirish: {warning_text}")
    except Exception:
        pass
async def add_admin(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    args = message.get_args().strip()
    if not args.isdigit():
        await message.answer("Foydalanish: /addadmin <user_id>")
        return
    user_id = int(args)
    data = load_data()
    if user_id in data.get('admins', []):
        await message.answer("Bu foydalanuvchi allaqachon admin.")
        return
    data['admins'].append(user_id)
    save_data(data)
    await message.answer(f"{user_id} admin sifatida qo‘shildi.")

async def remove_admin(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    args = message.get_args().strip()
    if not args.isdigit():
        await message.answer("Foydalanish: /removeadmin <user_id>")
        return
    user_id = int(args)
    data = load_data()
    if user_id not in data.get('admins', []):
        await message.answer("Bu foydalanuvchi admin emas.")
        return
    data['admins'].remove(user_id)
    save_data(data)
    await message.answer(f"{user_id} adminlikdan olib tashlandi.")

async def add_manager(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    args = message.get_args().strip()
    if not args.isdigit():
        await message.answer("Foydalanish: /addmanager <user_id>")
        return
    user_id = int(args)
    data = load_data()
    if user_id in data.get('managers', []):
        await message.answer("Bu foydalanuvchi allaqachon menejer.")
        return
    data['managers'].append(user_id)
    save_data(data)
    await message.answer(f"{user_id} menejer sifatida qo‘shildi.")

async def remove_manager(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    args = message.get_args().strip()
    if not args.isdigit():
        await message.answer("Foydalanish: /removemanager <user_id>")
        return
    user_id = int(args)
    data = load_data()
    if user_id not in data.get('managers', []):
        await message.answer("Bu foydalanuvchi menejer emas.")
        return
    data['managers'].remove(user_id)
    save_data(data)
    await message.answer(f"{user_id} menejerlikdan olib tashlandi.")
async def open_issues(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    data = load_data()
    issues = [i for i in data.get('issues', []) if i['status'] == 'open']
    if not issues:
        await message.answer("Ochiq muammolar yo‘q.")
        return
    text = "<b>Barcha ochiq muammolar:</b>\n"
    for i in issues:
        text += f"- Admin: {i['admin_id']} | {i['text']} | {time.strftime('%Y-%m-%d %H:%M', time.localtime(i['timestamp']))}\n"
    await message.answer(text, parse_mode="HTML")

async def all_penalties(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    data = load_data()
    penalties = data.get('penalties', [])
    if not penalties:
        await message.answer("Jarimalar yo‘q.")
        return
    text = "<b>Barcha jarimalar:</b>\n"
    for p in penalties:
        text += f"- Admin: {p['admin_id']} | {p['reason']} | {time.strftime('%Y-%m-%d %H:%M', time.localtime(p['timestamp']))}\n"
    await message.answer(text, parse_mode="HTML")

# /setlogin <admin_id> <login> <parol>
# Yoki: adminga reply qilib 
# /setlogin <login> <parol>
async def set_admin_login(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    args = message.get_args().split(maxsplit=2)
    admin_id = None
    login = None
    password = None
    # Variant 1: /setlogin <admin_id> <login> <parol>
    if len(args) >= 3:
        admin_id_s, login, password = args
        try:
            admin_id = int(admin_id_s)
        except ValueError:
            await message.answer("Admin ID raqam bo‘lishi kerak.")
            return
    # Variant 2: reply qilib /setlogin <login> <parol>
    elif len(args) >= 2 and getattr(message, 'reply_to_message', None):
        login, password = args
        admin_id = message.reply_to_message.from_user.id
    else:
        await message.answer("Foydalanish: /setlogin <admin_id> <login> <parol>\nYoki: adminga REPLY qilib /setlogin <login> <parol>")
        return
    data = load_data()
    if admin_id not in data.get('admins', []):
        await message.answer("Bunday admin mavjud emas.")
        return
    set_admin_credentials(admin_id, login, password)
    await message.answer("Kirish ma’lumotlari o‘rnatildi.")
    try:
        await message.bot.send_message(admin_id, f"Sizning tizimga kirish ma’lumotlaringiz:\nLogin: {login}\nParol: {password}\nBotda kirish: /login {login} {password}")
    except Exception:
        pass

async def list_admins(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    data = load_data()
    admins = data.get('admins', [])
    if not admins:
        await message.answer("Adminlar ro'yxati bo'sh.")
        return
    await message.answer("Adminlar ID ro'yxati:\n" + "\n".join(str(a) for a in admins))
async def statistics(message: types.Message):
    data = load_data()
    admin_count = len(data.get('admins', []))
    manager_count = len(data.get('managers', []))
    complaints = len(data.get('complaints', []))
    penalties = len(data.get('penalties', []))
    issues = len(data.get('issues', [])) if 'issues' in data else 0
    await message.answer(f"<b>Statistika:</b>\nAdminlar: {admin_count}\nMenejerlar: {manager_count}\nShikoyatlar: {complaints}\nJarimalar: {penalties}\nMuammolar: {issues}", parse_mode="HTML")
 


async def manager_panel(message: types.Message):
    if message.from_user.id in MANAGER_IDS:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        kb.add(
            KeyboardButton("/statistika"),
            KeyboardButton("/ochiqmuammolar"),
            KeyboardButton("/jarimalar"),
            KeyboardButton("/shikoyat"),
            KeyboardButton("/addadmin"),
            KeyboardButton("/removeadmin"),
            KeyboardButton("/addmanager"),
            KeyboardButton("/removemanager"),
            KeyboardButton("/blockadmin"),
            KeyboardButton("/unblockadmin"),
            KeyboardButton("/warnadmin")
        )
        await message.answer("Menejer paneliga xush kelibsiz!", reply_markup=kb)
    else:
        await message.answer("Sizda ruxsat yo'q.")

# /muammo <admin_id> <muammo matni>
async def send_issue(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        await message.answer("Sizda ruxsat yo'q.")
        return
    args = message.get_args().split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Foydalanish: /muammo <admin_id> <muammo matni>")
        return
    admin_id, issue_text = args[0], args[1]
    try:
        admin_id = int(admin_id)
    except ValueError:
        await message.answer("Admin ID raqam bo'lishi kerak.")
        return
    data = load_data()
    if admin_id not in data['admins']:
        await message.answer("Bunday admin mavjud emas.")
        return
    issue = {
        'admin_id': admin_id,
        'manager_id': message.from_user.id,
        'text': issue_text,
        'timestamp': int(time.time()),
        'status': 'open'
    }
    if 'issues' not in data:
        data['issues'] = []
    data['issues'].append(issue)
    save_data(data)
    await message.answer(f"Muammo admin ({admin_id}) uchun saqlandi va monitoringga qo'shildi.")

# /shikoyat <admin_id> <matn> — menejer tomonidan adminga shikoyat yaratish
async def create_complaint(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        await message.answer("Sizda ruxsat yo'q.")
        return
    args = message.get_args().split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Foydalanish: /shikoyat <admin_id> <matn>")
        return
    admin_id_s, text = args
    try:
        admin_id = int(admin_id_s)
    except ValueError:
        await message.answer("Admin ID raqam bo‘lishi kerak.")
        return
    data = load_data()
    if admin_id not in data.get('admins', []):
        await message.answer("Bunday admin mavjud emas.")
        return
    comp = {
        'admin_id': admin_id,
        'manager_id': message.from_user.id,
        'text': text,
        'timestamp': int(time.time()),
        'status': 'open',
        'responses': []
    }
    if 'complaints' not in data:
        data['complaints'] = []
    data['complaints'].append(comp)
    save_data(data)
    await message.answer("Shikoyat saqlandi.")
    # Adminni xabardor qilishga urinish
    try:
        await message.bot.send_message(admin_id, f"Sizga yangi shikoyat: {text}\nID: {comp['timestamp']}. Javob berish: /javob {comp['timestamp']} <matn>")
    except Exception:
        pass

async def issue_resolved(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    # /hal_boldi_<timestamp>
    if message.text.startswith("/hal_boldi_"):
        ts = message.text.replace("/hal_boldi_", "").strip()
        data = load_data()
        for issue in data.get('issues', []):
            if str(issue['timestamp']) == ts and issue['status'] == 'open':
                issue['status'] = 'resolved_by_manager'
                save_data(data)
                await message.answer("Muammo hal bo‘ldi deb belgilandi.")
                return
        await message.answer("Muammo topilmadi yoki allaqachon yopilgan.")

async def issue_rejected(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    # /rad_<timestamp>
    if message.text.startswith("/rad_"):
        ts = message.text.replace("/rad_", "").strip()
        data = load_data()
        for issue in data.get('issues', []):
            if str(issue['timestamp']) == ts and issue['status'] == 'open':
                issue['status'] = 'rejected'
                # Jarima yozish
                penalty = {
                    'admin_id': issue['admin_id'],
                    'manager_id': message.from_user.id,
                    'reason': f"Muammo hal qilinmadi: {issue['text']}",
                    'timestamp': int(time.time())
                }
                if 'penalties' not in data:
                    data['penalties'] = []
                data['penalties'].append(penalty)
                save_data(data)
                await message.answer("Admin uchun jarima yozildi va muammo rad etildi.")
                return
        await message.answer("Muammo topilmadi yoki allaqachon yopilgan.")

# /shikoyat_yop <complaint_id>
async def close_complaint(message: types.Message):
    if message.from_user.id not in MANAGER_IDS:
        return
    comp_id = message.get_args().strip()
    if not comp_id:
        await message.answer("Foydalanish: /shikoyat_yop <complaint_id>")
        return
    data = load_data()
    for c in data.get('complaints', []):
        if str(c['timestamp']) == comp_id and c['manager_id'] == message.from_user.id and c.get('status') == 'open':
            c['status'] = 'closed'
            save_data(data)
            await message.answer("Shikoyat yopildi.")
            return
    await message.answer("Shikoyat topilmadi yoki allaqachon yopilgan.")

def register_manager_handlers(dp: Dispatcher):
    dp.register_message_handler(manager_panel, commands=["manager"])
    dp.register_message_handler(send_issue, commands=["muammo"])
    dp.register_message_handler(create_complaint, commands=["shikoyat"])
    dp.register_message_handler(issue_resolved, regexp=r"^/hal_boldi_\d+")
    dp.register_message_handler(issue_rejected, regexp=r"^/rad_\d+")
    dp.register_message_handler(statistics, commands=["statistika"])
    dp.register_message_handler(open_issues, commands=["ochiqmuammolar"])
    dp.register_message_handler(all_penalties, commands=["jarimalar"])
    dp.register_message_handler(set_admin_login, commands=["setlogin"])
    dp.register_message_handler(list_admins, commands=["listadmins"])
    dp.register_message_handler(close_complaint, commands=["shikoyat_yop"])
    dp.register_message_handler(add_admin, commands=["addadmin"])
    dp.register_message_handler(remove_admin, commands=["removeadmin"])
    dp.register_message_handler(add_manager, commands=["addmanager"])
    dp.register_message_handler(remove_manager, commands=["removemanager"])
    dp.register_message_handler(block_admin, commands=["blockadmin"])
    dp.register_message_handler(unblock_admin, commands=["unblockadmin"])
    dp.register_message_handler(warn_admin, commands=["warnadmin"])
    dp.register_message_handler(my_profile, commands=["profil"])
    dp.register_message_handler(export_csv, commands=["exportcsv"])
    # Inline tugmalar o‘rniga reply keyboard ishlatilmoqda, shu sabab callback handler ro‘yxatdan chiqarildi

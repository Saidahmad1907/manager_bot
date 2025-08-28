# Manager Accessory Bot

Telegram uchun menejer va adminlar faoliyatini boshqaruvchi professional bot.

## Xususiyatlar
- Menejer va adminlar uchun alohida panellar (inline tugmalar bilan)
- Muammo, shikoyat, jarima, ogohlantirish va bloklash funksiyalari
- Faoliyat statistikasi va shaxsiy profil
- CSV eksport va haftalik hisobot
- Avtomatik monitoring va eskalatsiya
- Rollarni boshqarish (admin/menejer qo‘shish yoki olib tashlash)

## O‘rnatish va ishga tushirish

1. **Python va kutubxonalarni o‘rnating**
   - Python 3.8+
   - `pip install aiogram`

2. **Loyihani yuklab oling yoki klonlang**

3. **Bot tokenini va admin/menejer ID-larini sozlang**
   - `config.py` faylini oching
   - `TOKEN` ga o‘z bot tokeningizni yozing
   - `MANAGER_IDS` va `ADMIN_IDS` ro‘yxatiga kerakli Telegram user ID-larni kiriting

4. **Botni ishga tushiring**
   - Konsolda:
     ```bash
     python main.py
     ```

5. **Botdan foydalanish**
   - Menejer va adminlar /manager yoki /admin komandasi orqali panelga kiradi
   - Barcha asosiy funksiyalar inline tugmalar va komandalar orqali ishlaydi

## Asosiy komandalar

### Menejerlar uchun:
- /manager — menejer paneli
- /addadmin <user_id> — admin qo‘shish
- /removeadmin <user_id> — admin olib tashlash
- /addmanager <user_id> — menejer qo‘shish
- /removemanager <user_id> — menejer olib tashlash
- /blockadmin <user_id> — adminni bloklash
- /unblockadmin <user_id> — adminni blokdan chiqarish
- /warnadmin <user_id> <matn> — ogohlantirish
- /muammo <admin_id> <matn> — admin uchun muammo yozish
- /ochiqmuammolar — barcha ochiq muammolar
- /jarimalar — barcha jarimalar
- /statistika — umumiy statistika
- /profil — shaxsiy menejer profili
- /exportcsv — barcha faoliyatni CSV faylga eksport qilish

### Adminlar uchun:
- /admin — admin paneli
- /shikoyat <matn> — shikoyat yuborish
- /muammolarim — o‘ziga biriktirilgan muammolar
- /muammo_hal <timestamp> — muammoni hal qilish
- /tarix — muammo va jarimalar tarixi
- /statistika — umumiy statistika
- /profil — shaxsiy admin profili

## Avtomatik funksiyalar
- 12 soat ichida muammo hal qilinmasa, menejerdan so‘raladi
- 24 soat ichida hal qilinmasa, barcha menejerlarga eskalatsiya xabari yuboriladi
- Har hafta admin va menejerlarga haftalik hisobot yuboriladi

## Foydali maslahatlar
- Foydalanuvchi ID-larni olish uchun @userinfobot yoki Telegram API-dan foydalaning
- Botni serverda doimiy ishlatish uchun pm2, supervisor yoki systemd kabi vositalardan foydalaning

## Muallif va yordam
Savollar yoki takliflar uchun: @yourusername

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.client import phone_kb, location_kb, tariff_kb, route_kb
from keyboards.menu import role_inline_kb, client_main_menu, driver_main_menu
from database.db import add_order, get_online_drivers_by_route, set_user_role, get_user_role, get_driver

router = Router()

class OrderTaxi(StatesGroup):
    waiting_for_route = State()
    waiting_for_phone = State()
    waiting_for_pickup = State()
    waiting_for_dropoff = State()
    waiting_for_tariff = State()

@router.message(Command("start"))
async def start_cmd(message: types.Message):
    role = await get_user_role(message.from_user.id)
    if not role:
        welcome_text = (
            "✨ **Chortoq Express Taxi — Ishonchli yo'ldoshingiz!** ✨\n\n"
            "Toshkent va Chortoq o'rtasida tez, qulay va xavfsiz safar qiling. "
            "Yo'lovchi yoki haydovchi sifatida xizmatimizdan foydalanishingiz mumkin.\n\n"
            "⚡️ **Afzalliklarimiz:**\n"
            "• ⏱ Tezkor haydovchi/yo'lovchi topish\n"
            "• 🚖 Hamyonbop va sifatli tariflar\n"
            "• 🛡 Ishonchli va tekshirilgan haydovchilar\n\n"
            "Davom etish uchun o'zingizga mos rolni tanlang 👇"
        )
        await message.answer(welcome_text, reply_markup=role_inline_kb)
    elif role == "client":
        await message.answer("🙋‍♂️ **Chortoq Express Taxi — Yo'lovchi menyusi:**", reply_markup=client_main_menu)
    elif role == "driver":
        await message.answer("🚖 **Chortoq Express Taxi — Haydovchi menyusi:**", reply_markup=driver_main_menu)

# 🆘 YORDAM BO'LIMI
@router.message(F.text == "🆘 Yordam / Qo'llab-quvvatlash")
async def help_handler(message: types.Message):
    help_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Admin bilan bog'lanish", url="https://t.me/Zefor02")],
            [InlineKeyboardButton(text="📞 Qo'llab-quvvatlash markazi", callback_data="+998947184345")]
        ]
    )
    
    help_text = (
        "🛠 **YORDAM VA QO'LLAB-QUVVATLASH MARKAZI**\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "❓ **Yo'lovchilar uchun:**\n"
        "• Taksi chaqirish tugmasini bosing va manzilingizni tanlang.\n"
        "• Buyurtmangiz faol haydovchilarga yuboriladi va tez orada biriktiriladi.\n\n"
        "❓ **Haydovchilar uchun:**\n"
        "• Liniyaga chiqish uchun 'Haydovchi kabineti' orqali holatingizni '🟢 Men ishdaman' ga o'tkazing.\n"
        "• Haftalik 20 000 so'm obunani 'Obunani uzaytirish' bo'limi orqali to'lab borishingiz kerak.\n\n"
        "☎️ Muammo yoki takliflar bo'lsa, admin bilan bog'lanishingiz mumkin."
    )
    await message.answer(help_text, reply_markup=help_kb)

@router.callback_query(F.data == "call_support")
async def support_call_info(callback: types.CallbackQuery):
    await callback.answer("📞 Qo'llab-quvvatlash telefon raqami: +998 90 123 45 67", show_alert=True)

@router.message(F.text == "🔄 Rolni o'zgartirish")
async def change_role(message: types.Message):
    await message.answer("🎭 O'zingizga kerakli yangi rolni tanlang:", reply_markup=role_inline_kb)

@router.callback_query(F.data.startswith("role_"))
async def process_role_selection(callback: types.CallbackQuery, state: FSMContext):
    selected_role = callback.data.split("_")[1]
    await set_user_role(callback.from_user.id, selected_role)
    
    if selected_role == "client":
        await callback.message.edit_text("✅ Siz **Yo'lovchi (Mijoz)** rolini tanladingiz!")
        await callback.message.answer("📍 Yo'lovchi menyusi:", reply_markup=client_main_menu)
    else:
        await callback.message.edit_text("✅ Siz **Haydovchi** rolini tanladingiz!")
        driver = await get_driver(callback.from_user.id)
        if not driver:
            await callback.message.answer("🚘 Haydovchilikni boshlash uchun avval ro'yxatdan o'ting.\n\n'🚗 Haydovchi kabineti' tugmasini bosing.", reply_markup=driver_main_menu)
        else:
            await callback.message.answer("🚖 Haydovchi menyusi:", reply_markup=driver_main_menu)
    await callback.answer()

@router.message(F.text == "🚖 Taksi chaqirish")
async def start_order(message: types.Message, state: FSMContext):
    role = await get_user_role(message.from_user.id)
    if role != "client":
        await message.answer("⚠️ Taksi chaqirish faqat mijozlar uchun amal qiladi.")
        return
        
    await state.set_state(OrderTaxi.waiting_for_route)
    await message.answer("🗺 **Qaysi yo'nalish bo'yicha ketmoqchisiz?**", reply_markup=route_kb)

@router.callback_query(OrderTaxi.waiting_for_route, F.data.startswith("route_"))
async def process_route(callback: types.CallbackQuery, state: FSMContext):
    route_name = "Chortoqdan Toshkentga" if callback.data == "route_chortoq_toshkent" else "Toshkentdan Chortoqqa"
    await state.update_data(route=route_name)
    
    await state.set_state(OrderTaxi.waiting_for_phone)
    await callback.message.answer(
        f"📍 Yo'nalish: **{route_name}**\n\n📱 Buyurtma uchun **telefon raqamingizni** yuboring:",
        reply_markup=phone_kb
    )
    await callback.answer()

@router.message(OrderTaxi.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    
    await state.set_state(OrderTaxi.waiting_for_pickup)
    await message.answer("📍 Olib ketish manzilini yuboring (lokatsiya yoki matn ko'rinishida):", reply_markup=location_kb)

@router.message(OrderTaxi.waiting_for_pickup)
async def process_pickup(message: types.Message, state: FSMContext):
    if message.location:
        pickup = f"https://maps.google.com/?q={message.location.latitude},{message.location.longitude}"
    else:
        pickup = message.text
        
    await state.update_data(pickup=pickup)
    await state.set_state(OrderTaxi.waiting_for_dropoff)
    await message.answer("🏁 Boradigan aniq manzilingizni yozing:", reply_markup=types.ReplyKeyboardRemove())

@router.message(OrderTaxi.waiting_for_dropoff)
async def process_dropoff(message: types.Message, state: FSMContext):
    await state.update_data(dropoff=message.text)
    await state.set_state(OrderTaxi.waiting_for_tariff)
    await message.answer("🚖 O'zingizga ma'qul tarifni tanlang:", reply_markup=tariff_kb)

@router.callback_query(OrderTaxi.waiting_for_tariff, F.data.startswith("tariff_"))
async def process_tariff(callback: types.CallbackQuery, state: FSMContext):
    tariff_type = "Ekonom" if callback.data == "tariff_ekonom" else "Premium"
    price = "150 000 so'm" if tariff_type == "Ekonom" else "180 000 so'm"
    
    user_data = await state.get_data()
    full_pickup = f"[{user_data['route']}] {user_data['pickup']}"
    
    order_id = await add_order(
        client_id=callback.from_user.id,
        pickup=full_pickup,
        dropoff=user_data['dropoff'],
        price=f"{tariff_type} - {price}"
    )
    
    await state.clear()
    
    await callback.message.edit_text(
        f"🎉 **BUYURTMANGIZ QABUL QILINDI! #{order_id}**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🗺 **Yo'nalish:** {user_data['route']}\n"
        f"📱 **Telefon:** {user_data['phone']}\n"
        f"📍 **Qayerdan:** {user_data['pickup']}\n"
        f"🏁 **Qayerga:** {user_data['dropoff']}\n"
        f"🚕 **Tarif:** {tariff_type} ({price})\n\n"
        f"⏳ *Haydovchi biriktirilmoqda, iltimos kuting...*"
    )
    await callback.message.answer("Asosiy menyu:", reply_markup=client_main_menu)
    
    matched_drivers = await get_online_drivers_by_route(user_data['route'])
    accept_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Buyurtmani olish", callback_data=f"accept_{order_id}")]
        ]
    )
    
    for driver_id in matched_drivers:
        try:
            await callback.bot.send_message(
                chat_id=driver_id,
                text=(
                    f"🚨 **YANGI BUYURTMA! #{order_id}**\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"🗺 **Yo'nalish:** {user_data['route']}\n"
                    f"📱 **Tel:** {user_data['phone']}\n"
                    f"📍 **Qayerdan:** {user_data['pickup']}\n"
                    f"🏁 **Qayerga:** {user_data['dropoff']}\n"
                    f"💰 **Narxi:** {price} ({tariff_type})"
                ),
                reply_markup=accept_kb
            )
        except Exception as e:
            print(f"Xatolik: {e}")

    await callback.answer()
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import (
    register_driver, get_driver, update_driver_status, assign_order,
    is_driver_paid, renew_subscription, get_order, cancel_order_db
)
from keyboards.client import phone_kb
from keyboards.menu import driver_main_menu

router = Router()

driver_status_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🟢 Men ishdaman", callback_data="status_online"),
            InlineKeyboardButton(text="🔴 Men ishni to'xtatdim", callback_data="status_offline")
        ],
        [InlineKeyboardButton(text="💳 Obunani uzaytirish (20 000 so'm)", callback_data="pay_subscription")]
    ]
)

driver_route_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚖 Chortoqdan Toshkentga", callback_data="droute_Chortoqdan Toshkentga")],
        [InlineKeyboardButton(text="🚖 Toshkentdan Chortoqqa", callback_data="droute_Toshkentdan Chortoqqa")]
    ]
)

class DriverRegister(StatesGroup):
    waiting_for_phone = State()
    waiting_for_driver_photo = State()
    waiting_for_car_model = State()
    waiting_for_car_number = State()
    waiting_for_car_photo = State()

def get_cabinet_text(driver):
    if not driver:
        return "⚠️ Haydovchi ma'lumotlari topilmadi. Qayta ro'yxatdan o'ting."
        
    user_handle = f"@{driver[2]}" if len(driver) > 2 and driver[2] and driver[2] != "Mavjud emas" else "Yo'q"
    phone = driver[1] if len(driver) > 1 and driver[1] else "Mavjud emas"
    car_model = driver[4] if len(driver) > 4 and driver[4] else "Mavjud emas"
    car_number = driver[5] if len(driver) > 5 and driver[5] else "Mavjud emas"
    
    paid_status = driver[11][:10] if len(driver) > 11 and driver[11] else "Tugagan"
    status_text = f"🟢 Online (Yo'nalish: {driver[10]})" if len(driver) > 10 and driver[9] == 'online' else "🔴 Offline (Ish to'xtatilgan)"
    
    return (
        f"🚖 **Haydovchi kabineti**\n\n"
        f"👤 Username: {user_handle}\n"
        f"📞 Tel: {phone}\n"
        f"🚘 Mashina: {car_model} ({car_number})\n"
        f"📅 Obuna muddati: **{paid_status}** gacha\n"
        f"📊 Holat: {status_text}\n\n"
        f"Kerakli tugmani tanlang:"
    )

@router.message(F.text == "🚗 Haydovchi kabineti")
async def driver_menu(message: types.Message, state: FSMContext):
    driver = await get_driver(message.from_user.id)
    if not driver:
        await state.set_state(DriverRegister.waiting_for_phone)
        await message.answer("📱 Ro'yxatdan o'tish uchun **telefon raqamingizni** yuboring:", reply_markup=phone_kb)
    else:
        await message.answer(get_cabinet_text(driver), reply_markup=driver_status_kb)

# Ro'yxatdan o'tish zanjiri
@router.message(DriverRegister.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    await state.set_state(DriverRegister.waiting_for_driver_photo)
    await message.answer("📸 O'zingizning **rasmingizni** yuboring:", reply_markup=types.ReplyKeyboardRemove())

@router.message(DriverRegister.waiting_for_driver_photo, F.photo)
async def process_driver_photo(message: types.Message, state: FSMContext):
    await state.update_data(driver_photo=message.photo[-1].file_id)
    await state.set_state(DriverRegister.waiting_for_car_model)
    await message.answer("🚘 **Mashinangiz rusumini** kiriting:")

@router.message(DriverRegister.waiting_for_car_model)
async def process_car_model(message: types.Message, state: FSMContext):
    await state.update_data(car_model=message.text)
    await state.set_state(DriverRegister.waiting_for_car_number)
    await message.answer("🔢 Mashinangizning **davlat raqamini** kiriting:")

@router.message(DriverRegister.waiting_for_car_number)
async def process_car_number(message: types.Message, state: FSMContext):
    await state.update_data(car_number=message.text)
    await state.set_state(DriverRegister.waiting_for_car_photo)
    await message.answer("📷 Endi **mashinangiz rasmini** yuboring:")

@router.message(DriverRegister.waiting_for_car_photo, F.photo)
async def process_car_photo(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    username = message.from_user.username if message.from_user.username else "Mavjud emas"
    
    await register_driver(
        user_id=message.from_user.id,
        phone=user_data['phone'],
        username=username,
        driver_photo=user_data['driver_photo'],
        car_model=user_data['car_model'],
        car_number=user_data['car_number'],
        car_photo=message.photo[-1].file_id
    )
    
    await state.clear()
    driver = await get_driver(message.from_user.id)
    await message.answer("🎉 **Tabriklaymiz, ro'yxatdan o'tdingiz!**", reply_markup=driver_main_menu)
    await message.answer(get_cabinet_text(driver), reply_markup=driver_status_kb)

# 🟢 Men ishdaman -> Obuna tekshiruvi
@router.callback_query(F.data == "status_online")
async def ask_driver_route(callback: types.CallbackQuery):
    paid = await is_driver_paid(callback.from_user.id)
    if not paid:
        pay_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💳 To'lovni amalga oshirish (20 000 so'm)", callback_data="pay_subscription")]
            ]
        )
        await callback.message.edit_text(
            "⚠️ **Haftalik to'lov muddati tugagan!**\n\n"
            "Buyurtmalarni qabul qilish uchun 20 000 so'm haftalik to'lovni amalga oshiring. To'lovsiz botdan foydalanib bo'lmaydi.",
            reply_markup=pay_kb
        )
        await callback.answer("Obuna muddati tugagan!", show_alert=True)
        return

    await callback.message.edit_text("🗺 **Qaysi yo'nalishda qatnaysiz?**", reply_markup=driver_route_kb)
    await callback.answer()

# 💳 Obuna va Karta ma'lumotlarini ko'rsatish
@router.callback_query(F.data == "pay_subscription")
async def show_payment_info(callback: types.CallbackQuery):
    pay_info_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ To'lov qildim (Tasdiqlash)", callback_data="confirm_payment")],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_cabinet")]
        ]
    )
    await callback.message.edit_text(
        "💳 **Haftalik obuna to'lovi (20 000 so'm)**\n\n"
        "To'lovni amalga oshirish uchun quyidagi karta raqamiga **20 000 so'm** o'tkazing:\n\n"
        "💳 **Karta raqami:** `8600 0000 0000 0000`\n"
        "👤 **Karta egasi:** Samandar T.\n"
        "💰 **Summa:** 20 000 so'm (7 kunlik obuna)\n\n"
        "O'tkazmani bajargach, pastdagi **'✅ To'lov qildim (Tasdiqlash)'** tugmasini bosing.",
        reply_markup=pay_info_kb
    )
    await callback.answer()

# To'lovni tasdiqlab, obunani uzaytirish
@router.callback_query(F.data == "confirm_payment")
async def process_payment_confirm(callback: types.CallbackQuery):
    await renew_subscription(callback.from_user.id, days=7)
    driver = await get_driver(callback.from_user.id)
    
    if driver:
        await callback.message.edit_text(
            "✅ **To'lovingiz qabul qilindi va obunangiz 7 kunga uzaytirildi!**\n\n" + get_cabinet_text(driver),
            reply_markup=driver_status_kb
        )
    else:
        await callback.message.edit_text("✅ To'lov qabul qilindi! Iltimos, kabinetni qayta oching.")
        
    await callback.answer("7 kunlik obuna faollashtirildi!", show_alert=True)

# Kabinetga qaytish
@router.callback_query(F.data == "back_to_cabinet")
async def back_to_cabinet_handler(callback: types.CallbackQuery):
    driver = await get_driver(callback.from_user.id)
    if driver:
        await callback.message.edit_text(get_cabinet_text(driver), reply_markup=driver_status_kb)
    await callback.answer()

# Yo'nalish tanlash
@router.callback_query(F.data.startswith("droute_"))
async def set_driver_route(callback: types.CallbackQuery):
    route_name = callback.data.split("_")[1]
    await update_driver_status(callback.from_user.id, "online", route_name)
    
    driver = await get_driver(callback.from_user.id)
    await callback.message.edit_text(get_cabinet_text(driver), reply_markup=driver_status_kb)
    await callback.answer(f"🟢 {route_name} yo'nalishi faollashtirildi!")

# 🔴 Ishni to'xtatish
@router.callback_query(F.data == "status_offline")
async def set_driver_offline(callback: types.CallbackQuery):
    await update_driver_status(callback.from_user.id, "offline", None)
    driver = await get_driver(callback.from_user.id)
    await callback.message.edit_text(get_cabinet_text(driver), reply_markup=driver_status_kb)
    await callback.answer("🔴 Ish to'xtatildi!")

# Buyurtmani qabul qilish
@router.callback_query(F.data.startswith("accept_"))
async def accept_order_handler(callback: types.CallbackQuery):
    order_id = int(callback.data.split("_")[1])
    driver_id = callback.from_user.id
    
    success = await assign_order(order_id, driver_id)
    
    if success:
        order = await get_order(order_id)
        driver = await get_driver(driver_id)
        client_id = order[1]
        
        cancel_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Buyurtmani bekor qilish", callback_data=f"cancel_{order_id}")]
            ]
        )
        
        await callback.message.edit_text(
            f"✅ **Buyurtma #{order_id} qabul qilindi!**\n\n"
            f"📍 Manzil: {order[3]}\n"
            f"🏁 Borish: {order[4]}\n"
            f"💰 Narxi: {order[5]}\n\n"
            f"Mijoz bilan bog'laning!",
            reply_markup=cancel_kb
        )
        
        driver_handle = f"@{driver[2]}" if driver and len(driver) > 2 and driver[2] != "Mavjud emas" else "Mavjud emas"
        client_text = (
            f"🚖 **Sizga haydovchi biriktirildi!**\n\n"
            f"👤 Haydovchi: {driver_handle}\n"
            f"📞 Tel: {driver[1] if driver else 'Mavjud emas'}\n"
            f"🚘 Mashina: {driver[4] if driver else 'Mavjud emas'}\n"
            f"🔢 Raqam: {driver[5] if driver else 'Mavjud emas'}"
        )
        
        try:
            await callback.bot.send_photo(
                chat_id=client_id,
                photo=driver[3],
                caption=client_text,
                reply_markup=cancel_kb
            )
        except Exception:
            await callback.bot.send_message(
                chat_id=client_id,
                text=client_text,
                reply_markup=cancel_kb
            )
            
        await callback.answer("Buyurtma olindi!")
    else:
        await callback.message.edit_text("❌ Bu buyurtmani boshqa haydovchi olib bo'ldi!")
        await callback.answer("Kechikdingiz!", show_alert=True)

# Buyurtmani bekor qilish
@router.callback_query(F.data.startswith("cancel_"))
async def cancel_order_handler(callback: types.CallbackQuery):
    order_id = int(callback.data.split("_")[1])
    order = await get_order(order_id)
    
    if not order or order[6] == 'cancelled':
        await callback.answer("Buyurtma allaqachon bekor qilingan!", show_alert=True)
        return
        
    await cancel_order_db(order_id)
    
    client_id = order[1]
    driver_id = order[2]
    
    try:
        await callback.bot.send_message(chat_id=client_id, text=f"❌ **Buyurtma #{order_id} bekor qilindi.**")
    except Exception:
        pass
        
    if driver_id:
        try:
            await callback.bot.send_message(chat_id=driver_id, text=f"❌ **Buyurtma #{order_id} bekor qilindi.**")
        except Exception:
            pass

    await callback.message.edit_text(f"❌ Buyurtma #{order_id} bekor qilindi.")
    await callback.answer("Buyurtma bekor qilindi!")
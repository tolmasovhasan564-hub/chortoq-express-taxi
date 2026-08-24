from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# 1. Yo'nalish tanlash tugmalari (Inline)
route_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚖 Chortoqdan Toshkentga", callback_data="route_chortoq_toshkent")],
        [InlineKeyboardButton(text="🚖 Toshkentdan Chortoqqa", callback_data="route_toshkent_chortoq")]
    ]
)

# 2. Telefon raqam yuborish tugmasi
phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# 3. Lokatsiya yuborish tugmasi
location_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Lokatsiyamni yuborish", request_location=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# 4. Tarif tanlash tugmalari (Inline)
tariff_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚖 Ekonom — 150 000 so'm", callback_data="tariff_ekonom")],
        [InlineKeyboardButton(text="🚘 Premium — 180 000 so'm", callback_data="tariff_premium")]
    ]
)
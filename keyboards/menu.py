from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Asosiy menyu
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚖 Taksi chaqirish")],
        [KeyboardButton(text="🚗 Haydovchi kabineti")],
        [KeyboardButton(text="🆘 Yordam / Qo'llab-quvvatlash")],
        [KeyboardButton(text="🔄 Rolni o'zgartirish")]
    ],
    resize_keyboard=True
)

# Startdagi rol tanlash tugmalari
role_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🚖 Haydovchi bo'lish", callback_data="role_driver"),
            InlineKeyboardButton(text="🙋‍♂️ Yo'lovchi bo'lish", callback_data="role_client")
        ]
    ]
)

# Yo'lovchi menyusi
client_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚖 Taksi chaqirish")],
        [KeyboardButton(text="🆘 Yordam / Qo'llab-quvvatlash")],
        [KeyboardButton(text="🔄 Rolni o'zgartirish")]
    ],
    resize_keyboard=True
)

# Haydovchi menyusi
driver_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚗 Haydovchi kabineti")],
        [KeyboardButton(text="🆘 Yordam / Qo'llab-quvvatlash")],
        [KeyboardButton(text="🔄 Rolni o'zgartirish")]
    ],
    resize_keyboard=True
)
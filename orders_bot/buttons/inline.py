from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup




def main_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Buyurtma raqami bo'yicha qidirish", callback_data="check_order_number"),
        ],
    ])
    return keyboard

def back_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="back"),
        ],
    ])
    return keyboard

def change_order_status_keyboard(order_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Kutilmoqda", callback_data=f"status_pending_{order_id}"),
            InlineKeyboardButton(text="Yetkazilmoqda", callback_data=f"status_delivering_{order_id}"),
        ],
        [
            InlineKeyboardButton(text="Yetkazib berildi", callback_data=f"status_delivered_{order_id}"),
            InlineKeyboardButton(text="Bekor qilindi", callback_data=f"status_cancelled_{order_id}"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="back"),
        ]
    ])
    return keyboard
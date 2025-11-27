from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,WebAppInfo
from orders_bot.models import ChannelsToSubscribe
from orders_bot.utils import remove_at_prefix

def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛍️ Do'konga kirish", web_app=WebAppInfo(url="https://toysmars.uz/")),
            InlineKeyboardButton(text="🛒 Savatcha", callback_data="view_cart"),
        ],
        [
            InlineKeyboardButton(text="👤 Profile", callback_data="view_profile"),
            InlineKeyboardButton(text="ℹ️ Ma'lumot", callback_data="view_info"),
            
        ]
    ])
    return keyboard

def admin_keyboard() -> InlineKeyboardMarkup:
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


def join_channels():
    channels = ChannelsToSubscribe.objects.all()

    buttons = [
        [InlineKeyboardButton(
            text=channel.name,
            url=f"https://t.me/{remove_at_prefix(channel.link)}"
        )] for channel in channels
    ]

    buttons.append([InlineKeyboardButton(
        text="✅ Check",
        callback_data="check_subscription"
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


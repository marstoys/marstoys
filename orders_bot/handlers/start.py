from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, BotCommand
from aiogram.filters import Command
from django.utils import timezone
from django.core.paginator import Paginator
from orders_bot.models import  TelegramAdminsID
from orders_bot.dispatcher import dp, bot
from shop.models import Order

@dp.message(Command("start"))
async def start(message: Message) -> None:
    if not TelegramAdminsID.objects.filter(tg_id=message.from_user.id).exists():
        TelegramAdminsID.objects.create(tg_id=message.from_user.id)
    await message.answer("Assalomu alaykum. Bu bot sizga Buyurtmalarni avtomatik yuborib boradi.")


@dp.message(Command("all"))
async def send_all_orders(message: Message):
    msg, keyboard = generate_order_list_message(page=1)
    await message.answer(msg, reply_markup=keyboard, parse_mode="HTML")


@dp.callback_query(F.data.startswith("orders_page_"))
async def orders_pagination_handler(callback_query: CallbackQuery):
    page = int(callback_query.data.split("_")[-1])
    msg, keyboard = generate_order_list_message(page=page)

    await callback_query.message.edit_text(
        msg,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback_query.answer()


def generate_order_list_message(page: int = 1, per_page: int = 5):
    orders = Order.objects.all().order_by('-created_at')
    paginator = Paginator(orders, per_page)
    page_obj = paginator.get_page(page)

    if not orders.exists():
        return "Hozircha hech qanday zayafka mavjud emas.", None

    msg = f"📋 <b>Barcha zayafkalar</b> (Sahifa {page}/{paginator.num_pages})\n\n"

    for i, order in enumerate(page_obj, start=1 + (page - 1) * per_page):
        msg += (
            f"#{i}\n"
            f"👤 Ism: {order}\n"
            f"📞 Tel: {order.phone}\n"
            f"🛠 O'rnatib berish bilan: {'✅' if order.service_included else '❌'}\n"
            f"🕒 Sana: {timezone.localtime(order.created_at).strftime('%Y-%m-%d %H:%M')}\n\n"
        )


    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"orders_page_{page - 1}"))
    if page < paginator.num_pages:
        navigation_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"orders_page_{page + 1}"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[navigation_buttons]) if navigation_buttons else None
    return msg, keyboard


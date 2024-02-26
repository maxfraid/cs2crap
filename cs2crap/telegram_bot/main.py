import asyncio
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.filters.state import State, StatesGroup

from cs2crap.telegram_bot.utils import get_bot_data
from cs2crap.common.utils import color_print, print_cscrap_logo
from cs2crap.common.main import update_database, cscrap


BOT_TOKEN, TELEGRAM_API_URL, CHAT_ID = get_bot_data()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

STM2STM_ENABLED = True
CSM2STM_ENABLED = False
STM2CSM_ENABLED = True

stop_cscrap_event = asyncio.Event()

buttons = [
    [
        types.KeyboardButton(text="/cscrap"),
    ],
    [
        types.KeyboardButton(text="/update"),
        types.KeyboardButton(text="/stop"),
        types.KeyboardButton(text="/methods"),
    ],
    [
        types.KeyboardButton(text="/stm2stm"),
        types.KeyboardButton(text="/csm2stm"),
        types.KeyboardButton(text="/stm2csm"),
    ],
]

commands_keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# ==================================================================================================================================
# |                                                           TELEGRAM BOT                                                         |
# ==================================================================================================================================


async def starting_message():
    await bot.send_message(
        CHAT_ID,
        rf"""🚀 *Бот запущен* 🚀

🧰 *Включенные методы*:
{"\n- *Steam* to *Steam*" if STM2STM_ENABLED else ""}{"\n- *CS:GO Market* to *Steam*" if CSM2STM_ENABLED else ""}{"\n- *Steam* to *CS:GO Market*" if STM2CSM_ENABLED else ""}""",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=commands_keyboard,
    )


# ==================================================================================================================================


@dp.message(Command("stm2stm"))
async def toggle_stm2stm(message: types.Message):
    global STM2STM_ENABLED
    STM2STM_ENABLED = not STM2STM_ENABLED
    color_print(
        "status",
        "status",
        f'Steam -> Steam {"включен" if STM2STM_ENABLED else "выключен"}',
        True,
    )
    await message.answer(
        f"🎮 *Steam* to *Steam* {'*включен* 🎮' if STM2STM_ENABLED else '*выключен* 🎮'}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=commands_keyboard,
    )


@dp.message(Command("csm2stm"))
async def toggle_csm2stm(message: types.Message):
    global CSM2STM_ENABLED
    CSM2STM_ENABLED = not CSM2STM_ENABLED
    color_print(
        "status",
        "status",
        f'CS:GO Market -> Steam {"включен" if CSM2STM_ENABLED else "выключен"}',
        True,
    )
    await message.answer(
        f"💰 *CS:GO Market* to *Steam* {'*включен* 💰' if CSM2STM_ENABLED else '*выключен* 💰'}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=commands_keyboard,
    )


@dp.message(Command("stm2csm"))
async def toggle_stm2csm(message: types.Message):
    global STM2CSM_ENABLED
    STM2CSM_ENABLED = not STM2CSM_ENABLED
    color_print(
        "status",
        "status",
        f'Steam -> CS:GO Market {"включен" if STM2CSM_ENABLED else "выключен"}',
        True,
    )
    await bot.send_message(
        CHAT_ID,
        f"💼 *Steam* to *CS:GO Market* {'*включен* 💼' if STM2CSM_ENABLED else '*выключен* 💼'}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=commands_keyboard,
    )


# ==================================================================================================================================


@dp.message(Command("methods"))
async def toggle_stm2csm(message: types.Message):
    (
        await message.answer(
            f"""🧰 *Включенные методы*: 🧰
{"\n- *Steam* to *Steam*" if STM2STM_ENABLED else ""}{"\n- *CS:GO Market* to *Steam*" if CSM2STM_ENABLED else ""}{"\n- *Steam* to *CS:GO Market*" if STM2CSM_ENABLED else ""}""",
            parse_mode=ParseMode.MARKDOWN,
        )
        if STM2STM_ENABLED or CSM2STM_ENABLED or STM2CSM_ENABLED
        else await message.answer(
            f"""🧰 *Нет включенных методов* 🧰""",
            parse_mode=ParseMode.MARKDOWN,
        )
    )


@dp.message(Command("update"))
async def update_items_database(message: types.Message):
    await message.answer(
        "🔄 *Обновление базы предметов* 🔄",
        parse_mode=ParseMode.MARKDOWN,
    )

    update_database()

    await message.answer(
        "✨ *База данных обновлена* ✨",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=commands_keyboard,
    )


class CScrapForm(StatesGroup):
    waiting_for_price_range = State()


@dp.message(StateFilter(None), Command("cscrap"))
async def start_cscrap_command(message: types.Message, state: FSMContext):
    await message.answer(
        "⚙️ *Введите диапазон цен* (например, *100-200*):",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=types.ForceReply(),
    )
    await state.set_state(CScrapForm.waiting_for_price_range)


@dp.message(StateFilter(CScrapForm.waiting_for_price_range))
async def run_cscrap(message: types.Message, state: FSMContext):
    lower_price = None
    upper_price = None

    try:
        args_text = message.text.strip()

        if args_text == "all":
            price_range = None
        else:
            lower_price, upper_price = map(int, args_text.split("-"))
            price_range = (lower_price, upper_price)

        await state.clear()

        await message.answer(
            rf"""🚀 *Поиск предметов запущен!* 🚀

🧰 *Методы:*
{"\n- *Steam* to *Steam*" if STM2STM_ENABLED else ""}{"\n- *CS:GO Market* to *Steam*" if CSM2STM_ENABLED else ""}{"\n- *Steam* to *CS:GO Market*" if STM2CSM_ENABLED else ""}

🤑 *Ценовой диапазон:* {(f"*{lower_price}* - *{upper_price}*") if lower_price is not None and upper_price is not None else "all"}""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=commands_keyboard,
        )

        stop_cscrap_event.clear()

        loop = asyncio.get_event_loop()
        try:
            if price_range is not None:
                await loop.run_in_executor(
                    None,
                    cscrap,
                    price_range,
                    STM2STM_ENABLED,
                    CSM2STM_ENABLED,
                    STM2CSM_ENABLED,
                    stop_cscrap_event,
                )
            else:
                await loop.run_in_executor(
                    None,
                    cscrap,
                    None,
                    STM2STM_ENABLED,
                    CSM2STM_ENABLED,
                    STM2CSM_ENABLED,
                    stop_cscrap_event,
                )
        except Exception as e:
            print("Ошибка при запуске cscrap:", e)

        await message.answer(
            f"🌌 *Поиск предметов завершён* 🌌",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=commands_keyboard,
        )
    except (Exception, UnboundLocalError, ValueError) as e:
        await message.answer(
            """Неправильный формат команды.
Используйте:
- /cscrap lower_price-upper_price (определённый диапазон цен)
- /cscrap all (все предметы)""",
            reply_markup=commands_keyboard,
        )


@dp.message(Command("stop"))
async def stop_cscrap(message: types.Message):
    stop_cscrap_event.set()


# ==================================================================================================================================


async def main():
    """
    Главный цикл бота
    """
    print_cscrap_logo()

    while True:
        try:
            await starting_message()
            await dp.start_polling(bot)
            break
        except Exception as e:
            color_print("fail", "fail", f"Ошибка соединения: {e}", True)
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())

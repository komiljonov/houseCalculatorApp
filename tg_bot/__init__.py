from io import BytesIO

from django.core.files.base import File
from telegram import Bot, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ExtBot,
    MessageHandler,
    PicklePersistence,
    filters,
)

from bot.models import User
from constants import BACK, CREDIT_DURATION, HOME_PRICE, MENU, PERCENT_PER_YEAR, STARTUP_PRICE
from utils import ReplyKeyboardMarkup


class Bot:
    def __init__(self, token: str):
        self.token = token

        self.app = ApplicationBuilder().token(self.token).concurrent_updates(128).build()

        self.app.add_handler(
            ConversationHandler(
                [
                    CommandHandler('start', self.start)
                ],
                {
                    MENU: [
                        MessageHandler(filters.Text(
                            ["Kalkulator"]), self.calculator)
                    ],
                    HOME_PRICE: [
                        MessageHandler(filters.Regex(
                            r"^\d+$"), self.home_price),
                            MessageHandler(filters.Text([BACK]),self.start)
                    ],
                    STARTUP_PRICE: [
                        MessageHandler(filters.Regex(
                            r"^\d+$"), self.startup_price),
                            MessageHandler(filters.Text([BACK]),self.calculator)

                    ],
                    PERCENT_PER_YEAR: [
                        MessageHandler(filters.Regex(r"^\d+$"),
                                       self.percent_per_year),
                        MessageHandler(filters.Text([BACK]),self.back_from_percent_per_year)

                    ],
                    CREDIT_DURATION: [

                        MessageHandler(filters.Regex(r"^\d+$"),
                                       self.credit_duration),
                        MessageHandler(filters.Text([BACK]),self.back_from_credit_duration)
                    ]
                },
                [

                ],
                name="MainConversation"
            )
        )

        self.app.run_polling()

    async def start(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        await tgUser.send_message("Assalomu aleykum. Xush kelibsiz.", reply_markup=ReplyKeyboardMarkup([
            [
                "Kalkulator",
                # "Savol berish"
            ]
        ]))

        return MENU

    async def calculator(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        await tgUser.send_message("Olinayotgan uy narxini kiriting.")
        return HOME_PRICE

    async def home_price(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        temp.home_price = int(update.message.text)
        temp.save()
        await tgUser.send_message("Boshlang'ich to'lovni kiriting.")
        return STARTUP_PRICE

    async def startup_price(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        temp.startup_price = int(update.message.text)
        temp.save()
        await tgUser.send_message("Yillik foyizni kiriting.")

        return PERCENT_PER_YEAR

    async def percent_per_year(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        temp.percent_per_year = int(update.message.text)
        temp.save()
        await tgUser.send_message("Kredit muddatini kiriting.")

        return CREDIT_DURATION

    async def credit_duration(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        temp.credit_duration = int(update.message.text)
        temp.save()

        b = temp.home_price - temp.startup_price

        z = temp.percent_per_year / 100
        f = b * z * temp.credit_duration

        b = b + f
        res = b // (temp.credit_duration*12)

        await tgUser.send_message(f"Oylik to'lov: {res:,}")
        return await self.start(update, context)






    async def back_from_percent_per_year(self,update:Update,context:CallbackContext):
        tgUser, user, temp = User.get(update)
        await tgUser.send_message("Boshlang'ich to'lovni kiriting.")
        return STARTUP_PRICE




    async def back_from_credit_duration(self,update:Update,context:CallbackContext):
        tgUser, user, temp = User.get(update)
        await tgUser.send_message("Yillik foyizni kiriting.")

        return PERCENT_PER_YEAR

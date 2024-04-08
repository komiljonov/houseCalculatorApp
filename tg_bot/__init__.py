from io import BytesIO

from django.core.files.base import File
from telegram import Bot, Update, Message
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

from bot.models import Question, User
from constants import BACK, CREDIT_DURATION, EXCLUDE, HOME_PRICE, MENU, PERCENT_PER_YEAR, STARTUP_PRICE,QUESTION
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
                            ["Kalkulator"]), self.calculator),
                        #MessageHandler(filters.Text(
                        #    ["Savol berish"]), self.question)
                    ],
                    HOME_PRICE: [
                        MessageHandler(filters.Regex(
                            r"^\d+$"), self.home_price),
                        MessageHandler(filters.Text([BACK]), self.start)
                    ],
                    STARTUP_PRICE: [
                        MessageHandler(filters.Regex(
                            r"^\d+$"), self.startup_price),
                        MessageHandler(filters.Text([BACK]), self.calculator)

                    ],
                    # PERCENT_PER_YEAR: [
                    #     MessageHandler(filters.Regex(r"^\d+$"),
                    #                    self.percent_per_year),
                    #     MessageHandler(filters.Text([BACK]),self.back_from_percent_per_year)

                    # ],
                    # CREDIT_DURATION: [

                    #     MessageHandler(filters.Regex(r"^\d+$"),
                    #                    self.credit_duration),
                    #     MessageHandler(filters.Text([BACK]),self.back_from_credit_duration)
                    # ],
                    QUESTION: [
                        MessageHandler(filters.TEXT & EXCLUDE,
                                       self.question_text)
                    ]
                },
                [
                    CommandHandler('start', self.start)
                ],
                name="MainConversation"
            )
        )

        self.app.add_handler(
            MessageHandler(filters.ChatType.GROUP & filters.REPLY &
                           filters.TEXT & EXCLUDE, self.group_question_answer)
        )
        self.app.add_handler(
            MessageHandler(filters.ChatType.PRIVATE & filters.REPLY &
                           filters.TEXT & EXCLUDE, self.group_question_answer_user)
        )

        self.app.run_polling()

    async def start(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        await tgUser.send_message("Assalomu aleykum. Xush kelibsiz.", reply_markup=ReplyKeyboardMarkup([
            [
                "Kalkulator",
                #"Savol berish"
            ]
        ]))

        return MENU

    async def calculator(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        await tgUser.send_message("Siz `Yangi Hayot` uylarini 18% bilan,\n"
                                  "20 yil kridet muddatiga olishingiz mumkun!")

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
        temp.percent_per_year = 18
        temp.credit_duration = 20
        temp.save()

        b = temp.home_price - temp.startup_price

        z = temp.percent_per_year / 100
        f = b * z * temp.credit_duration

        b = b + f
        res = b // (temp.credit_duration*12)

        await tgUser.send_message(f"Oylik to'lov: {res:,}")
        return await self.start(update, context)

    # async def percent_per_year(self, update: Update, context: CallbackContext):
    #     tgUser, user, temp = User.get(update)

    #     temp.percent_per_year = int(update.message.text)
    #     temp.save()
    #     await tgUser.send_message("Kredit muddatini kiriting.")

    #     return CREDIT_DURATION

    # async def credit_duration(self, update: Update, context: CallbackContext):
    #     tgUser, user, temp = User.get(update)

    #     temp.credit_duration = int(update.message.text)
    #     temp.save()

    #     b = temp.home_price - temp.startup_price

    #     z = temp.percent_per_year / 100
    #     f = b * z * temp.credit_duration

    #     b = b + f
    #     res = b // (temp.credit_duration*12)

    #     await tgUser.send_message(f"Oylik to'lov: {res:,}")
    #     return await self.start(update, context)

    # async def back_from_percent_per_year(self,update:Update,context:CallbackContext):
    #     tgUser, user, temp = User.get(update)
    #     await tgUser.send_message("Boshlang'ich to'lovni kiriting.")
    #     return STARTUP_PRICE

    # async def back_from_credit_duration(self,update:Update,context:CallbackContext):
    #     tgUser, user, temp = User.get(update)
    #     await tgUser.send_message("Yillik foyizni kiriting.")

    #     return PERCENT_PER_YEAR

    async def question(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        await tgUser.send_message("Iltimos savolingizni yuboring.", reply_markup=ReplyKeyboardMarkup())

        return QUESTION

    async def question_text(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        text = update.message.text

        group_message: Message = await update.get_bot().send_message(
            -4162149949,
            "Yangi savol.\n\n"
            f"Id: {user.chat_id}\n"
            f"Ism: {user.name}\n"
            f"Tg Ismi: {tgUser.full_name}\n"
            f"Text: {text}"

        )

        new_question = Question.objects.create(
            user=user,
            message=text,
            user_message_id=update.message.message_id,
            group_message_id=group_message.message_id
        )

        await tgUser.send_message("Sizning savolingiz yuborildi.\n\nIltimos javob berishlarini kuting.")

        return await self.start(update, context)

    async def group_question_answer(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        question = Question.objects.filter(
            group_message_id=update.message.reply_to_message.message_id).first()

        if not question:
            return

        user_message: Message = (await update.get_bot().send_message(
            question.user.chat_id,
            update.message.text,
            reply_to_message_id=question.user_message_id
        ))

        new_question = Question.objects.create(
            user=user,
            message=update.message.text,
            user_message_id=user_message.message_id,
            group_message_id=update.message.message_id,
            sender=2
        )

    async def group_question_answer_user(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        question = Question.objects.filter(
            user_message_id=update.message.reply_to_message.message_id).first()

        if not question:
            return

        group_message: Message = (await update.get_bot().send_message(
            -4162149949,
            "Javobga javob.\n\n"
            f"Id: {user.chat_id}\n"
            f"Ism: {user.name}\n"
            f"Tg Ismi: {tgUser.full_name}\n"
            f"Text: {update.message.text}",
            reply_to_message_id=question.group_message_id
        ))

        new_question = Question.objects.create(
            user=user,
            message=update.message.text,
            # user_message_id=user_message.message_id,
            # group_message_id=update.message.message_id,
            user_message_id=update.message.message_id,
            group_message_id=group_message.message_id
        )

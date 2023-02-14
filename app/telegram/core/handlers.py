import time
import telebot
import logging
import schedule
from threading import Thread
from logging.handlers import RotatingFileHandler
from app.telegram.core import data
from app.telegram.schedule.data import TEXT_BUTTON_NOW, TEXT_BUTTON_DAY, TEXT_BUTTON_WEEK
from app.telegram.admin.data import SUPERADMIN_LIST
from app.telegram.schedule.controller import get_user, get_full_user

bot = telebot.TeleBot(token=data.TOKEN)


main_markup = telebot.types.ReplyKeyboardMarkup(True)
main_markup.add(TEXT_BUTTON_NOW, TEXT_BUTTON_DAY, TEXT_BUTTON_WEEK)

commands = [
    telebot.types.BotCommand("start", "starts innoSchedule bot"),
    telebot.types.BotCommand("help", "Overview of bot commands"),
    telebot.types.BotCommand("profile", "View my profile information"),
    telebot.types.BotCommand("config_schedule", "Configure group settings"),
    telebot.types.BotCommand("add_elective", "Add an elective course"),
    telebot.types.BotCommand(
        "rm_electives", "Clear all registered elective courses"),
    telebot.types.BotCommand("config_remind", "Configure reminder settings"),
    telebot.types.BotCommand("link", "Visit the official course schedule"),
    telebot.types.BotCommand(
        "week_number", "Week number by the academic calendar"),
    telebot.types.BotCommand(
        "config_optional", "Configure optional courses e.g Russian Lang."),
    telebot.types.BotCommand(
        "feedback", "Flag inaccurate information(Be as precise as possible)"),
]
# log configuration
logger = logging.getLogger(data.LOG_NAME)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(data.LOG_FILE_NAME, maxBytes=data.LOG_MAX_SIZE_BYTES,
                              backupCount=data.LOG_BACKUP_COUNT)
handler.setFormatter(logging.Formatter(
    data.LOG_MESSAGE_FORMAT, data.LOG_DATE_FORMAT))
logger.addHandler(handler)


def log(module, message):
    if message.from_user.username:
        user = message.from_user.username
    else:
        user = str(message.from_user.id)
    logger.info(f"{module.rjust(15)} :: {user.rjust(20)} ::"
                f"{message.text if message.text else '--not_text--'}")


def attach_core_module():

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        log(data.MODULE_NAME, message)
        if message.text == "/start":
            print(f"USER {message.from_user.id} clicked start")
            bot.send_message(message.chat.id, data.MESSAGE_HI,
                             reply_markup=main_markup)
        elif message.text == "/help":
            print(f"USER {message.from_user.id} clicked help")
            bot.send_message(message.chat.id, data.MESSAGE_HELP,
                             reply_markup=main_markup)

    @bot.message_handler(commands=['feedback'])
    def send_feedback(message):
        log(data.MODULE_NAME, message)
        if message.text == "/feedback":
            print(f"USER {message.from_user.id} wants to send feedback")
            msg = bot.send_message(message.chat.id, data.FEEDBACK_PROMPT,
                                   reply_markup=main_markup)
            bot.register_next_step_handler(msg, process_feedback_step)

    @bot.message_handler(commands=['profile'])
    def view_profile(message):
        log(data.MODULE_NAME, message)
        print(f"USER {message.from_user.id} wants to see profile")
        user = get_full_user(message.from_user.id)
        if not user:
            return
        elective_courses = user.elective_courses
        elective_abbrevations = list(
            map(lambda course: course.short_name, elective_courses))

        optional_course = user.optional_course
        reply = f"GROUP - {user.main_group.specific_group if user.main_group else 'NOT SET'}" + \
            f"\nELECTIVE - {', '.join(elective_abbrevations) if elective_courses else 'NOT SET'}" + \
            f"\nOPTIONAL COURSE - {optional_course.short_name if optional_course else 'NOT SET'}" + \
            f"\nREMINDER - {'ON' if user.remind_me else 'OFF'}"
        bot.send_message(message.chat.id, reply,
                         reply_markup=main_markup)

    def process_feedback_step(message):
        log(data.MODULE_NAME, message)

        if not message.text:
            bot.send_message(message.chat.id, data.MESSAGE_ERROR,
                             reply_markup=main_markup)
            return

        user = get_user(message.from_user.id)
        if not user:
            return
        alias = user.handle if user.handle else user.id
        feedback = message.text
        for admin in SUPERADMIN_LIST:
            bot.send_message(
                admin, f"{data.MESSAGE_FEEDBACK} {str(alias)}:\n{feedback}")
        bot.send_message(message.chat.id, data.FEEDBACK_SUCCESS,
                         reply_markup=main_markup)


def compose_attached_modules(set_proxy=False):

    @bot.message_handler()
    def garbage_message_handler(message):
        """
        Fallback handler for unknown messages
        To be called after all other modules have mounted their handlers
        """
        log(data.MODULE_NAME, message)
        # You could implement chatgpt or just Q&A over here
        bot.send_message(message.chat.id, data.MESSAGE_ERROR,
                         reply_markup=main_markup)
        user = get_user(message.from_user.id)
        if not user:
            return
        alias = user.handle if user.handle else user.id
        for admin in SUPERADMIN_LIST:
            bot.send_message(
                admin, f"{data.MESSAGE_UNKNOWN} {str(alias)}:\n{message.text}")

    def polling_telegram_bot_commands():
        print("Bot begins polling")
        bot.infinity_polling(long_polling_timeout=5, timeout=10)

    def pending_schedule():
        # Verify schedule if some action should be made
        while True:
            schedule.run_pending()
            time.sleep(1)

    bot.delete_my_commands()
    bot.set_my_commands(commands=commands)
    Thread(target=polling_telegram_bot_commands, daemon=True).start()
    Thread(target=pending_schedule, daemon=True).start()

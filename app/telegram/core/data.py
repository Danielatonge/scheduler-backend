MODULE_NAME = "core"

# TOKEN = "625620708:AAFII7HO_Anlcn0pLMUN9Y_HNkTDJ0MLctc"  # - worksilently_bot
# TOKEN = "6057962313:AAEEDkC3cDA0j3JQBsqr6FlMorSPzXQ7uvs"  # - test_inno_schedule_bot
TOKEN = "1360816203:AAFGwIslhxZJmYIQsjAa2GxX1COhJ21vnG4"  # - inno_schedule_bot

MESSAGE_HI = "Hi there!✋"
MESSAGE_HELP = "Schedule platform for Innopolis students.\n\n" \
               "Some useful commands:\n" \
               "/config_schedule - change group settings\n" \
    "/add_elective - add an elective course\n" \
    "/rm_electives - clear all registered elective courses\n" \
    "/config_remind - change reminders settings\n" \
    "/link - visit the official course schedule\n" \
    "/week_number - week number by the academic calendar\n" \
    "/profile - view my profile information\n" \
    "/config_optional - configure optional courses e.g Russian Lang.\n" \
    "/feedback - flag inaccurate information(Be as precise as possible)\n" \
               "/help\n\n" \
               "Inspired by: https://gitlab.com/Louie_ru/InnoSchedule\n" \
               "Big thanks to @Nmikriukov and @thedownhill\n" \
               "For any issues or requests, contact @hardriive"
MESSAGE_ERROR = "Sorry, I did not understand you"
MESSAGE_UNKNOWN = "Unknown message from"
MESSAGE_FEEDBACK = "Feedback message from"
FEEDBACK_PROMPT = "Leave your feedback"
FEEDBACK_SUCCESS = "Your feedback was successfully received.\n"

LOG_FILE_NAME = 'log'
LOG_MAX_SIZE_BYTES = 1024 * 1024 * 10  # 10 MB
LOG_NAME = 'logger'
LOG_BACKUP_COUNT = 1
LOG_MESSAGE_FORMAT = "%(asctime)s :: %(message)s"
LOG_DATE_FORMAT = "%d.%m.%Y :: %H:%M:%S"

PROXY_PROTOCOL = 'https'
PROXY_SOCKS = 'socks5'
PROXY_LOGIN = '356819408'
PROXY_PASSWORD = 'nya8e4Es'
PROXY_ADDRESS = 'deimos.public.opennetwork.cc'
PROXY_PORT = '1090'

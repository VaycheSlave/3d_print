from telegram import Bot
from django.conf import settings
from printer.models import UserProfile

# Инициализация бота
bot = Bot(settings.TELEGRAM_BOT_TOKEN)

def handle_message(update):
    user_id = update.message.chat_id
    telegram_id = str(user_id)
    # Проверка существования профиля пользователя
    if UserProfile.objects.filter(telegram_id=telegram_id).exists():
        # Профиль уже существует, можно обновить дополнительные данные пользователя, если необходимо
        pass
    else:
        # Создание нового профиля пользователя
        user_profile = UserProfile.objects.create(telegram_id=telegram_id)
        # Дополнительные действия по инициализации профиля, если необходимо
        pass

# Установка вебхука (вызывается один раз при запуске приложения)
bot.set_webhook("https://yourdomain.com/path/to/telegram/webhook/")
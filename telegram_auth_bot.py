"""
Telegram бот для авторизации пользователей
Отправляет данные на Django API для получения токена авторизации
"""

import os
import logging
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, ContextTypes
except ImportError:
    print("❌ Установите python-telegram-bot: pip install python-telegram-bot")
    exit(1)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', "8565856173:AAFTypWFfOHVmCoZoI0jz68xn0gld6KToMU")
BOT_SECRET = os.getenv('TELEGRAM_BOT_SECRET', 'your-secret-key-change-this')
API_URL = os.getenv('API_URL', 'https://coated-trisha-nonvexatiously.ngrok-free.dev/accounts/api/v1')
DOMAIN = os.getenv('DOMAIN', 'coated-trisha-nonvexatiously.ngrok-free.dev')


async def create_login_token(user_data: dict) -> dict:
    """
    Отправка запроса на Django API для создания токена авторизации
    
    Args:
        user_data: Данные пользователя из Telegram
        
    Returns:
        dict: Ответ от API с login_url и токеном
    """
    url = f"{API_URL}/get-token/"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {BOT_TOKEN}'
    }
    
    payload = {
        'telegram_id': user_data['telegram_id'],
        'username': user_data.get('username', ''),
        'first_name': user_data['first_name'],
        'last_name': user_data.get('last_name', '')
    }
    
    logger.info(f"Отправка запроса на {url}")
    logger.info(f"Payload: {payload}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=10) as response:
                logger.info(f"Статус ответа: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Успешный ответ: {data}")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка API: {response.status} - {error_text}")
                    return None
                    
    except asyncio.TimeoutError:
        logger.error("Таймаут при запросе к API")
        return None
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка HTTP клиента: {e}")
        return None
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start
    
    1. Получает данные пользователя из Telegram
    2. Отправляет POST запрос на Django API /api/auth/create-token/
    3. Получает login_url в ответе
    4. Показывает кнопку "🌐 Войти на сайт" с этим URL
    """
    user = update.effective_user
    
    logger.info(f"Команда /start от пользователя: {user.id} (@{user.username})")
    
    # Формируем данные пользователя
    user_data = {
        'telegram_id': user.id,
        'username': user.username or '',
        'first_name': user.first_name or 'User',
        'last_name': user.last_name or ''
    }
    
    # Отправляем приветственное сообщение
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"⏳ Создаю токен авторизации...",
        parse_mode='HTML'
    )
    
    # Создаем токен через API
    api_response = await create_login_token(user_data)
    
    if not api_response:
        # Ошибка при создании токена
        await update.message.reply_text(
            "❌ <b>Ошибка</b>\n\n"
            "Не удалось создать токен авторизации.\n"
            "Попробуйте позже или обратитесь к администратору.\n\n"
            "Используйте /start для повторной попытки.",
            parse_mode='HTML'
        )
        return
    
    # Получаем login_url из ответа
    login_url = api_response.get('login_url')
    expires_at = api_response.get('expires_at')
    
    if not login_url:
        await update.message.reply_text(
            "❌ <b>Ошибка</b>\n\n"
            "Некорректный ответ от сервера.\n\n"
            "Используйте /start для повторной попытки.",
            parse_mode='HTML'
        )
        return
    
    # Создаем кнопку с login_url
    keyboard = [[
        InlineKeyboardButton(
            "🌐 Войти на сайт",
            url=login_url
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем сообщение с кнопкой
    message = (
        f"✅ <b>Токен создан!</b>\n\n"
        f"Нажмите кнопку ниже для входа на сайт.\n\n"
        f"⏱ Токен действителен <b>5 минут</b>\n"
        f"🔒 Токен одноразовый и безопасный\n\n"
        f"<i>После входа вы получите JWT токены для доступа к API</i>"
    )
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    
    logger.info(f"Токен создан для пользователя {user.id}, login_url отправлен")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "📚 <b>Помощь</b>\n\n"
        "<b>Команды:</b>\n"
        "/start - Начать авторизацию\n"
        "/help - Показать эту справку\n\n"
        "<b>Как это работает:</b>\n"
        "1. Отправьте /start\n"
        "2. Бот создаст токен авторизации\n"
        "3. Нажмите кнопку \"🌐 Войти на сайт\"\n"
        "4. Вы будете авторизованы и получите JWT токены\n\n"
        "<b>Безопасность:</b>\n"
        "• Токен действителен 5 минут\n"
        "• Токен одноразовый\n"
        "• Используется шифрование\n\n"
        f"<b>API:</b> {API_URL}"
    )
    
    await update.message.reply_text(help_text, parse_mode='HTML')


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке обновления: {context.error}", exc_info=context.error)
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Произошла ошибка при обработке вашего запроса.\n"
            "Попробуйте позже или используйте /help"
        )


def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        return
    
    logger.info("="*60)
    logger.info("🤖 Запуск Telegram бота для авторизации")
    logger.info("="*60)
    logger.info(f"📡 API URL: {API_URL}")
    logger.info(f"🌐 Domain: {DOMAIN}")
    logger.info(f"🔑 Bot Secret: {'*' * len(BOT_TOKEN)}")
    logger.info("="*60)
    logger.info("\n💡 Команды:")
    logger.info("   /start - Начать авторизацию")
    logger.info("   /help - Помощь")
    logger.info("\n⏹️  Нажмите Ctrl+C для остановки\n")
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)
    
    logger.info("✅ Бот запущен и готов к работе!")
    
    # Запускаем polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)

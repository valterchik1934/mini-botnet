from telethon import TelegramClient
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import (
    InputReportReasonSpam,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonOther,
)
import asyncio
import logging
import os
import re
from colorama import Fore, Style, init

# Инициализация colorama
init()

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Данные вашего приложения Telegram API
API_ID = "ВАШ_API_ID"  # Замените на ваш API ID
API_HASH = "ВАШ_API_HASH"  # Замените на ваш API Hash

# Папка для хранения сессий
SESSIONS_DIR = "sessions"

# Создаем папку для сессий, если её нет
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

# Список причин для жалоб
REASONS = {
    "1": InputReportReasonSpam(),
    "2": InputReportReasonViolence(),
    "3": InputReportReasonPornography(),
    "4": InputReportReasonOther(),
}

# Большая надпись с ником автора
BANNER = f"""
{Fore.RED}
██╗   ██╗ █████╗ ██╗  ████████╗███████╗██████╗  ██████╗██╗  ██╗
██║   ██║██╔══██╗██║  ╚══██╔══╝██╔════╝██╔══██╗██╔════╝██║ ██╔╝
██║   ██║███████║██║     ██║   █████╗  ██████╔╝██║     █████╔╝ 
╚██╗ ██╔╝██╔══██║██║     ██║   ██╔══╝  ██╔══██╗██║     ██╔═██╗ 
 ╚████╔╝ ██║  ██║███████╗██║   ███████╗██║  ██║╚██████╗██║  ██╗
  ╚═══╝  ╚═╝  ╚═╝╚══════╝╚═╝   ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
{Style.RESET_ALL}
{Fore.RED}Автор: VALTERCHIK{Style.RESET_ALL}
"""

# Знак автора
AUTHOR_SIGN = f"{Fore.RED}[VALTERCHIK]{Style.RESET_ALL}"


async def report_message(client, chat, message_id, reason):
    """Отправляет жалобу на сообщение."""
    try:
        await client(
            ReportRequest(
                peer=chat,
                id=[message_id],  # ID сообщения
                reason=reason,
                message="Это автоматическая жалоба.",
            )
        )
        logger.info(
            f"{AUTHOR_SIGN} {Fore.GREEN}Жалоба отправлена с аккаунта {client.session.filename} на сообщение {message_id} в чате {chat.title}.{Style.RESET_ALL}"
        )
    except Exception as e:
        logger.error(
            f"{AUTHOR_SIGN} {Fore.RED}Ошибка при отправке жалобы с аккаунта {client.session.filename}: {e}{Style.RESET_ALL}"
        )


async def add_account():
    """Добавляет новый аккаунт."""
    session_name = input(
        f"{AUTHOR_SIGN} {Fore.CYAN}Введите имя для новой сессии (например, account1): {Style.RESET_ALL}"
    )
    session_path = os.path.join(SESSIONS_DIR, session_name)

    # Создаем клиент для нового аккаунта
    client = TelegramClient(session_path, API_ID, API_HASH)
    try:
        await client.start()
        logger.info(
            f"{AUTHOR_SIGN} {Fore.GREEN}Аккаунт {session_name} успешно добавлен!{Style.RESET_ALL}"
        )
    except Exception as e:
        logger.error(
            f"{AUTHOR_SIGN} {Fore.RED}Ошибка при добавлении аккаунта {session_name}: {e}{Style.RESET_ALL}"
        )
    finally:
        await client.disconnect()


async def select_reason():
    """Выбирает причину жалобы."""
    print(f"\n{AUTHOR_SIGN} {Fore.YELLOW}Выберите причину жалобы:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}1. Спам{Style.RESET_ALL}")
    print(f"{Fore.CYAN}2. Насилие{Style.RESET_ALL}")
    print(f"{Fore.CYAN}3. Порнография{Style.RESET_ALL}")
    print(f"{Fore.CYAN}4. Другое{Style.RESET_ALL}")
    choice = input(f"{AUTHOR_SIGN} {Fore.CYAN}Введите номер причины: {Style.RESET_ALL}")
    return REASONS.get(choice, InputReportReasonOther())


def parse_message_link(link):
    """Парсит ссылку на сообщение."""
    pattern = r"https://t\.me/([^/]+)/(\d+)"
    match = re.match(pattern, link)
    if match:
        return match.group(1), int(match.group(2))  # username и ID сообщения
    return None, None


async def process_account(client, chat, message_ids, reason):
    """Обрабатывает аккаунт: отправляет жалобы на все указанные сообщения."""
    try:
        await client.start()
        for message_id in message_ids:
            await report_message(client, chat, message_id, reason)
    except Exception as e:
        logger.error(
            f"{AUTHOR_SIGN} {Fore.RED}Ошибка при обработке аккаунта {client.session.filename}: {e}{Style.RESET_ALL}"
        )
    finally:
        await client.disconnect()


async def main():
    """Основная функция."""
    # Получаем список всех сессий
    sessions = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".session")]

    if not sessions:
        logger.warning(
            f"{AUTHOR_SIGN} {Fore.YELLOW}Нет аккаунтов. Добавьте хотя бы один аккаунт.{Style.RESET_ALL}"
        )
        return

    # Запрашиваем ссылки на сообщения
    message_links = input(
        f"{AUTHOR_SIGN} {Fore.CYAN}Введите ссылки на сообщения через запятую: {Style.RESET_ALL}"
    ).split(",")

    # Парсим ссылки
    message_ids = []
    for link in message_links:
        chat_username, message_id = parse_message_link(link.strip())
        if chat_username and message_id:
            message_ids.append((chat_username, message_id))
        else:
            logger.warning(
                f"{AUTHOR_SIGN} {Fore.YELLOW}Неверная ссылка: {link.strip()}{Style.RESET_ALL}"
            )

    if not message_ids:
        logger.error(
            f"{AUTHOR_SIGN} {Fore.RED}Нет корректных ссылок на сообщения.{Style.RESET_ALL}"
        )
        return

    # Выбираем причину жалобы
    reason = await select_reason()

    # Создаем клиенты для каждого аккаунта
    clients = []
    for session in sessions:
        session_path = os.path.join(SESSIONS_DIR, session)
        client = TelegramClient(session_path, API_ID, API_HASH)
        clients.append(client)

    # Получаем информацию о чате (используем первый аккаунт)
    try:
        chat = await clients[0].get_entity(message_ids[0][0])
    except Exception as e:
        logger.error(
            f"{AUTHOR_SIGN} {Fore.RED}Ошибка при получении информации о чате: {e}{Style.RESET_ALL}"
        )
        return

    # Отправляем жалобы с каждого аккаунта
    tasks = []
    for client in clients:
        task = process_account(client, chat, [mid for _, mid in message_ids], reason)
        tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # Выводим баннер
    print(BANNER)

    # Основное меню
    print(f"{AUTHOR_SIGN} {Fore.CYAN}1. Добавить новый аккаунт{Style.RESET_ALL}")
    print(f"{AUTHOR_SIGN} {Fore.CYAN}2. Отправить жалобы{Style.RESET_ALL}")
    choice = input(f"{AUTHOR_SIGN} {Fore.CYAN}Выберите действие (1 или 2): {Style.RESET_ALL}")

    if choice == "1":
        asyncio.run(add_account())
    elif choice == "2":
        asyncio.run(main())
    else:
        print(f"{AUTHOR_SIGN} {Fore.RED}Неверный выбор.{Style.RESET_ALL}")


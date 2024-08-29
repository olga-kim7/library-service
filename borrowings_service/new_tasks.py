from datetime import timezone

from celery import shared_task, Celery
from django.contrib.sites import requests
from celery.beat import logger


from borrowings_service.models import Borrowing
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


app = Celery("telegram_bot", broker="redis://localhost")


@shared_task
def send_telegram_message(borrow_user: str):
    if borrow_user:
        message = f"There is a new borrowing from {borrow_user}"
        url = (
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
            f"/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
        )
        requests.get(url)


@shared_task
def check_overdue_borrowings():
    today = timezone.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today, actual_return_date__isnull=True
    )

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            user = borrowing.user
            book = borrowing.book
            message = f"Borrowing overdue! User: {user.first_name}, Book: {book.title}, Expected Return Date: {borrowing.expected_return_date}"
            send_telegram_message(message)
    else:
        send_telegram_message("No borrowings overdue today!")


def send_telegram_borrowed_task(borrowers_list: list):
    if len(borrowers_list) > 0:
        message = "There are/is borrowers\n"
        counter = 1
        for borrower in borrowers_list:
            user_email = borrower["borrower"]
            expiration = borrower["expiration"]
            message += f"{counter}. {user_email}" f" - overdue for {expiration} day/s\n"
            counter += 1
    else:
        message = "No borrowings overdue today!"
    try:
        url = (
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
            f"/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
        )
        response = requests.get(url)
        response.raise_for_status()
        logger.info(
            f"Telegram message sent successfully with status code "
            f"{response.status_code}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Telegram message: {e}")

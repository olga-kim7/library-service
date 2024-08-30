import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from books_service.models import Book
from borrowings_service.models import Borrowing, Payment
from users_service.models import User

BORROWING_URL = reverse("borrowings_service:borrowing-list")
PAYMENT_URL = reverse("borrowings_service:payment-list")


def get_borrowing_details(borrowing_id):
    return reverse("borrowings_service:borrowing-detail", args=[borrowing_id])


def sample_book(**params) -> Book:
    defaults = {
        "title": "Test Book",
        "author": "Test author",
        "cover": "hard",
        "inventory": 12,
        "daily_fee": 7,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_borrowing(user=None, book=None, **params):
    if user is None:
        user = get_user_model().objects.create_user(
            email="test@test.com",
            password="12345test",
        )
    if book is None:
        book = sample_book()
    default = {
        "expected_return_date": timezone.now() + datetime.timedelta(days=1),
        "borrow_date": datetime.date.today(),
        "book": book,
        "user": user,
    }
    default.update(params)
    return Borrowing.objects.create(**default)


def sample_payment(borrowing=None, **params):
    if borrowing is None:
        borrowing = sample_borrowing()
    default = {
        "status": "Pending",
        "type": "Payment",
        "borrowing_id": borrowing,
    }
    default.update(params)
    return Payment.objects.create(**default)


def get_payment_details(payment_id):
    return reverse("borrowings_service:payment-detail", args=[payment_id])


class TestUnAuthorizedViews(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=None)
        self.borrowing = sample_borrowing()

    def test_borrowing_list(self):
        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_borrowing_details(self):
        url = get_borrowing_details(self.borrowing.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payment_list(self):
        response = self.client.get(PAYMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payment_details(self):
        url = get_payment_details(self.borrowing.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAuthorizedViews(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            password="12345test",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.borrowing = sample_borrowing(
            user=self.user,
        )

    def test_get_money_to_pay(self):
        payment = Payment.objects.create(
            status="Pending",
            type="Payment",
            borrowing_id=self.borrowing,
        )
        self.borrowing.actual_return_date = timezone.now() + datetime.timedelta(days=1)
        self.borrowing.save()
        expected_charge = payment.get_money_to_pay
        self.assertEqual(payment.get_money_to_pay, expected_charge)

    def test_post_method_borrowings(self):
        book = sample_book(
            title="Test Books",
        )
        data = {
            "expected_return_date": timezone.now().date(),
            "borrow_date": timezone.now().date(),
            "book": book.id,
            "user": self.user.id,
        }
        response = self.client.post(BORROWING_URL, data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_method_borrowings(self):
        url = get_borrowing_details(self.borrowing.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

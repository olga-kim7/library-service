import datetime

from django.test import TestCase
from django.utils import timezone

from books_service.models import Book
from borrowings_service.models import Borrowing, Payment
from users_service.models import User


class BorrowingModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="Soft",
            inventory=10,
            daily_fee=10,
        )
        self.user = User.objects.create(email="test@test.com", password="12345test")
        self.borrowings = Borrowing.objects.create(
            borrow_date="2023-01-01",
            expected_return_date="2023-01-10",
            book=self.book,
            user=self.user,
        )

    def test_borrowings_str_method(self):
        self.assertEqual(
            str(self.borrowings),
            f"{self.borrowings.pk} "
            f"|Book: "
            f"{self.borrowings.book.title},"
            f" Borrowed at "
            f"{str(self.borrowings.borrow_date)}"
            f" - "
            f"{self.borrowings.user.email}",
        )


class TestPaymentsModel(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="Soft",
            inventory=10,
            daily_fee=10,
        )
        self.user = User.objects.create(email="test@test.com", password="12345test")
        self.borrowings = Borrowing.objects.create(
            expected_return_date=timezone.now() + datetime.timedelta(days=1),
            book=self.book,
            user=self.user,
            borrow_date=timezone.now(),
        )
        self.payments = Payment.objects.create(
            status="Pending", type="Payment", borrowing_id=self.borrowings
        )

    def test_payments_str_method(self):
        self.assertEqual(
            str(self.payments),
            f"payment: {self.payments.status}, "
            f"{self.payments.type},"
            f" {self.payments.borrowing_id}",
        )

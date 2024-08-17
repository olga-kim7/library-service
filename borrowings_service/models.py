import uuid

from django.db import models

from books_service.models import Book
from config import settings


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings")

    def __str__(self):
        return self.borrow_date


class Payment(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"

    class TypeChoices(models.TextChoices):
        PAYMENT = "PAYMENT"
        FINE = "FINE"

    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    type = models.CharField(max_length=20, choices=TypeChoices.choices)
    borrowing_id = models.ForeignKey(Borrowing, on_delete=models.CASCADE, related_name="payments")
    session_url = models.URLField(blank=True)
    session_id = models.TextField(blank=True)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

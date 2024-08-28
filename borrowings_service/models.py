from django.db import models
from rest_framework.exceptions import ValidationError

from books_service.models import Book
from config import settings


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    class Meta:
        verbose_name_plural = "Borrowings"

    def __str__(self):
        return (
            f"{self.pk} "
            f"|Book: {self.book.title},"
            f" Borrowed at {str(self.borrow_date)} - {self.user.email}"
        )

    def validate_book(self):
        if self.book.inventory == 0:
            raise ValidationError("there are no books in the inventory!")

    def clean(self):
        super().clean()
        self.validate_book()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"

    class TypeChoices(models.TextChoices):
        PAYMENT = "PAYMENT"
        FINE = "FINE"

    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )
    type = models.CharField(
        max_length=20, choices=TypeChoices.choices, default=TypeChoices.PAYMENT
    )
    borrowing_id = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField(blank=True, null=True)
    session_id = models.TextField(blank=True, null=True)

    @property
    def get_money_to_pay(self):
        return self.get_charge()

    def get_charge(self):
        borrow_day = self.borrowing_id.borrow_date
        return_day = self.borrowing_id.expected_return_date
        period = (return_day - borrow_day).days + 1
        return period * self.borrowing_id.book.daily_fee

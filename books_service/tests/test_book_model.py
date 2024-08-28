from django.test import TestCase

from books_service.models import Book


class BookModelTestCase(TestCase):
    def test_book_model_str(self):
        book_new = Book(
            title="Test Book",
            author="Test Autor",
            cover="HARD",
            inventory=12,
            daily_fee=5
        )
        self.assertEqual(str(book_new), book_new.title)

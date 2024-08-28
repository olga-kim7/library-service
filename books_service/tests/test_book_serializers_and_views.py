from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from books_service.models import Book
from books_service.serializers import BookSerializer

BOOK_LIST_URL = reverse("books_service:book-list")

BOOK_DETAIL = reverse("books_service:book-detail", kwargs={"pk": 1})


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


def get_books_retrieve(book_id):
    return reverse("books_service:book-detail", kwargs={"pk": book_id})


class AuthenticatedBookSerializerTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book = sample_book()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="12345test",
        )
        self.client.force_authenticate(self.user)

    def test_book_list_serializer(self):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        response = self.client.get(BOOK_LIST_URL)
        self.assertEqual(response.data, serializer.data)

    def test_book_retrieve_serializer(self):
        serializer = BookSerializer(self.book)
        url = get_books_retrieve(self.book.pk)
        response = self.client.get(url)
        self.assertEqual(response.data, serializer.data)


class UnauthenticatedBookAPITestCase(APITestCase):
    def setUp(self):
        self.book = sample_book()
        self.client = APIClient()
        self.client.force_authenticate(user=None)

    def test_unauthorized_required_book(self):
        url = get_books_retrieve(self.book.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_book_list(self):
        response = self.client.get(BOOK_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticatedBookAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.book = sample_book()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="12345test",
        )
        self.client.force_authenticate(self.user)

    def test_book_list_authenticated(self):
        response = self.client.get(BOOK_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_retrieve_authenticated(self):
        url = get_books_retrieve(self.book.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthorizedAminBookAPITestCase(APITestCase):
    def setUp(self):
        self.book = sample_book()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="12345test",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_post_book_method(self):
        data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "SOFT",
            "inventory": 12,
            "daily_fee": 7,
        }
        response = self.client.post(BOOK_LIST_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put_book_method(self):
        data = {
            "title": "Test Book2",
            "author": "Test Author2",
            "cover": "HARD",
            "inventory": 102,
            "daily_fee": 10,
        }

        url = get_books_retrieve(self.book.pk)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_book_method(self):
        url = get_books_retrieve(self.book.pk)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

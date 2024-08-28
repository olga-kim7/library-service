from datetime import timezone

import stripe
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction, IntegrityError
from django.shortcuts import redirect

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response

from books_service.models import Book
from borrowings_service.models import Borrowing, Payment
from borrowings_service.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    PaymentSerializer,
)
from config import settings
from config.settings import YOUR_DOMAIN

stripe.api_key = settings.STRIPE_SECRET_KEY


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all().select_related()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BorrowingSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingSerializer
        elif self.action == "list":
            return BorrowingListSerializer
        else:
            return BorrowingSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            return self.queryset.select_related()
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        # extra parameters added to the schema
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Active borrowings its borrowings where return day is None",
                required=False,
                type=str,
                examples=[
                    OpenApiExample(
                        "Example 1",
                        description="Find route with destination 'Gare do Oriente'",
                        value="true",
                    ),
                ],
            ),
            OpenApiParameter(
                name="user_id",
                description="Find borrowings by specific user. Only for administrators",
                required=False,
                type=str,
                examples=[
                    OpenApiExample(
                        "Example 1",
                        description="Find borrowings by specific user",
                        value="1",
                    ),
                ],
            ),
        ]
    )
    def list(self, requestre, *args, **kwargs):
        return super().list(requestre, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book_title = serializer.validated_data["book"]
        try:
            book = Book.objects.get(title=book_title)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except MultipleObjectsReturned:
            return Response(
                {"error": "Multiple books found with the same title"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if book.inventory <= 0:
            return Response(
                {"error": "Book is out of stock"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                book.inventory -= 1
                book.save()
        except IntegrityError:
            return Response(
                {"error": "Failed to update book inventory"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        borrowing = serializer.save()
        pay = Payment.objects.create(borrowing_id=borrowing)
        create_stripe_session(borrowing, pay)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()


def get_payment(payment: Payment):
    return payment.get_money_to_pay


def create_stripe_session(borrowing: Borrowing, pay: Payment):
    payment = get_payment(pay)
    price = stripe.Price.create(
        unit_amount=int(payment * 100),
        currency="usd",
        product_data={"name": f"Payment for borrowing {borrowing.book.title}"},
    )
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": borrowing.book.title,
                        },
                        "unit_amount": int(payment * 100),
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=YOUR_DOMAIN + "/success.html",
            cancel_url=YOUR_DOMAIN + "/cancel.html",
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    pay.session_url = session.url
    pay.session_id = session.id
    pay.save()
    return Response(session, status=status.HTTP_201_CREATED)


@shared_task
def get_paid_for_borrowing(payment_pk: int) -> None:
    pay = Payment.objects.get(id=payment_pk)
    pay.status = "Paid"
    pay.borrowing_id.actual_return_date = timezone.now().date()
    pay.borrowing_id.book.inventory += 1
    pay.borrowing_id.book.save()
    pay.borrowing_id.save()
    pay.save()

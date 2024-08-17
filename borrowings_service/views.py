from rest_framework import viewsets
from borrowings_service.models import Borrowing
from borrowings_service.serializers import BorrowingSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer


from django.urls import include, path
from rest_framework import routers

from borrowings_service.views import BorrowingViewSet, PaymentViewSet

router = routers.DefaultRouter()
router.register("borrowing", BorrowingViewSet)
router.register("payment", PaymentViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "borrowing_service"

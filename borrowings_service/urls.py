from django.urls import path, include
from rest_framework import routers

from borrowings_service.views import BorrowingViewSet

router = routers.DefaultRouter()
router.register("borrowing", BorrowingViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "borrowing_service"

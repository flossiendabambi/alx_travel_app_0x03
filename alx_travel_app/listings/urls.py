from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, PaymentViewSet, welcome

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', welcome, name='welcome'),          # Root is now welcome page
    path('api/', include(router.urls)),         # API under /api/
]

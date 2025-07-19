import os
import requests
from dotenv import load_dotenv
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Listing, Booking, Review, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from django.http import JsonResponse
from .tasks import send_booking_confirmation_email

def welcome(request):
    return render(request, 'welcome.html')


class ListingViewSet(viewsets.ModelViewSet):
    serializer_class = ListingSerializer
    queryset = Listing.objects.all()
    
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def perform_create(self, serializer):
        booking = serializer.save()
        send_booking_confirmation_email.delay(
            booking.user.email,
            booking.listing.title,
            booking.booking_date.strftime("%Y-%m-%d")
        )
    
load_dotenv()

CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY")
BASE_CALLBACK_URL = os.getenv("BASE_CALLBACK_URL")

    
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=False, methods=["post"])
    def initiate_payment(self, request):
        booking_reference = request.data.get("booking_reference")
        amount = request.data.get("amount")
        email = request.data.get("email")

        callback_url = f"{BASE_CALLBACK_URL}/api/verify-payment/"
        return_url = f"{BASE_CALLBACK_URL}/payment-success/"

        data = {
            "amount": amount,
            "currency": "ETB",
            "email": email,
            "tx_ref": booking_reference,
            "callback_url": callback_url,
            "return_url": return_url,
            "customization[title]": "Booking Payment",
            "customization[description]": "Payment for booking",
        }

        headers = {
            "Authorization": f"Bearer {CHAPA_SECRET_KEY}"
        }

        chapa_url = "https://api.chapa.co/v1/transaction/initialize"
        response = requests.post(chapa_url, json=data, headers=headers)

        if response.status_code == 200:
            res_data = response.json()
            # Save the Payment instance
            Payment.objects.create(
                booking_reference=booking_reference,
                amount=amount,
                email=email,
                transaction_id=res_data["data"]["tx_ref"],
                payment_status="Pending"
            )
            return Response(res_data, status=status.HTTP_200_OK)
        else:
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get", "post"])
    def verify_payment(self, request):
        tx_ref = request.data.get("tx_ref") or request.query_params.get("tx_ref")

        if not tx_ref:
            return Response({"error": "Missing tx_ref"}, status=400)

        verify_url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
        headers = {
            "Authorization": f"Bearer {CHAPA_SECRET_KEY}"
        }
        response = requests.get(verify_url, headers=headers)

        if response.status_code == 200 and response.json()["status"] == "success":
            status_ = response.json()["data"]["status"]
            Payment.objects.filter(transaction_id=tx_ref).update(payment_status=status_)
            return Response({"status": status_})
        return Response({"error": "Unable to verify"}, status=400)
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_booking_confirmation_email(email, listing_name, booking_date):
    subject = "Booking Confirmation"
    message = f"Thank you for booking {listing_name} on {booking_date}."
    from_email = "noreply@alxtravel.com"
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)

import uuid
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from listings.models import Listing, User

class Command(BaseCommand):
    help = "Seed the database with sample listings"

    def handle(self, *args, **kwargs):
        if not User.objects.exists():
            self.stdout.write(self.style.ERROR("No users found. Please create a user first."))
            return

        host_users = User.objects.filter(role='host')

        if not host_users.exists():
            self.stdout.write(self.style.ERROR("No hosts found. Please create users with role='host'."))
            return

        sample_data = [
            {
                "name": "Cozy Apartment in the City",
                "description": "A beautiful and modern apartment in the heart of downtown.",
                "location": "Downtown, New York",
                "price_per_night": 120.00,
            },
            {
                "name": "Beach House Retreat",
                "description": "Relaxing house by the beach with a great view.",
                "location": "Santa Monica, CA",
                "price_per_night": 250.00,
            },
            {
                "name": "Mountain Cabin Escape",
                "description": "A quiet cabin in the woods perfect for hiking and relaxing.",
                "location": "Aspen, CO",
                "price_per_night": 180.00,
            },
        ]

        for data in sample_data:
            listing = Listing.objects.create(
                listing_id=uuid.uuid4(),
                host=random.choice(host_users),
                name=data["name"],
                description=data["description"],
                location=data["location"],
                price_per_night=data["price_per_night"],
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            self.stdout.write(self.style.SUCCESS(f"Created listing: {listing.name}"))

        self.stdout.write(self.style.SUCCESS("✅ Database successfully seeded with sample listings."))
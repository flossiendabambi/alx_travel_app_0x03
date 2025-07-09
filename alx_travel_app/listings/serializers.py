from rest_framework import serializers
from .models import User, Listing, Booking, Review, Payment


# --- User Serializer ---
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'user_id',
            'first_name',
            'last_name',
            'email',
            'password_hash',
            'phone_number',
            'role',
            'created_at',
            'full_name'
        ]
        read_only_fields = ['user_id', 'created_at']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


# --- Listing Serializer ---
class ListingSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)

    class Meta:
        model = Listing
        fields = [
            'listing_id',
            'host',
            'name',
            'description',
            'location',
            'price_per_night',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['listing_id', 'created_at', 'updated_at']

    def validate_price_per_night(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


# --- Booking Serializer ---
class BookingSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'booking_id',
            'listing',
            'user',
            'start_date',
            'end_date',
            'total_price',
            'status',
            'created_at'
        ]
        read_only_fields = ['booking_id', 'created_at']

    def validate(self, data):
        if data['end_date'] <= data['start_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data


# --- Review Serializer ---
class ReviewSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            'review_id',
            'listing',
            'user',
            'rating',
            'comment',
            'created_at'
        ]
        read_only_fields = ['review_id', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "booking_reference",
            "transaction_id",
            "amount",
            "status",
            "created_at"
        ]
        read_only_fields = ["transaction_id", "payment_status", "created_at"]

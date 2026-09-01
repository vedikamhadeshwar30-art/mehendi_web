from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from .models import Service, Booking, GalleryItem, Review


class MehendiBookingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testbride',
            email='bride@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='Bride'
        )
        self.service = Service.objects.create(
            title='Royal Bridal Package',
            category='bridal',
            price=15000.00,
            duration_hours=4.0,
            description='Full bridal mehendi package'
        )
        self.target_date = timezone.now().date() + timedelta(days=5)

    def test_prevent_double_booking_model(self):
        """Test that booking the same date and time slot raises a validation error"""
        booking1 = Booking(
            service=self.service,
            customer_name='Client One',
            customer_email='client1@example.com',
            customer_phone='9876543210',
            booking_date=self.target_date,
            booking_time='09:00 AM',
            venue_type='studio'
        )
        booking1.save()

        # Attempt to book the exact same slot
        booking2 = Booking(
            service=self.service,
            customer_name='Client Two',
            customer_email='client2@example.com',
            customer_phone='9876543211',
            booking_date=self.target_date,
            booking_time='09:00 AM',
            venue_type='studio'
        )
        with self.assertRaises(ValidationError):
            booking2.save()

    def test_prevent_past_date_booking(self):
        """Test that booking a date in the past fails validation"""
        past_date = timezone.now().date() - timedelta(days=2)
        past_booking = Booking(
            service=self.service,
            customer_name='Past Client',
            customer_email='past@example.com',
            customer_phone='9876543210',
            booking_date=past_date,
            booking_time='09:00 AM',
            venue_type='studio'
        )
        with self.assertRaises(ValidationError):
            past_booking.save()

    def test_venue_travel_charge_calculation(self):
        """Test that home venue adds ₹500 travel surcharge"""
        home_booking = Booking(
            service=self.service,
            customer_name='Home Client',
            customer_email='home@example.com',
            customer_phone='9876543210',
            booking_date=self.target_date,
            booking_time='02:00 PM',
            venue_type='home',
            address='123 Marine Drive, Mumbai'
        )
        home_booking.save()
        self.assertEqual(home_booking.total_price, 15500.00)

    def test_api_available_slots(self):
        """Test that API accurately reports booked vs available slots"""
        Booking.objects.create(
            service=self.service,
            customer_name='Slot Holder',
            customer_email='slot@example.com',
            customer_phone='9876543210',
            booking_date=self.target_date,
            booking_time='09:00 AM',
            venue_type='studio'
        )

        response = self.client.get(reverse('api_available_slots'), {'date': self.target_date.strftime('%Y-%m-%d')})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['booked_count'], 1)
        
        # Check that 09:00 AM is not available
        slot_9am = next(s for s in data['slots'] if s['value'] == '09:00 AM')
        self.assertFalse(slot_9am['is_available'])

        # Check that 11:30 AM is available
        slot_1130am = next(s for s in data['slots'] if s['value'] == '11:30 AM')
        self.assertTrue(slot_1130am['is_available'])

    def test_booking_web_flow(self):
        """Test creating a booking via POST request"""
        post_data = {
            'service': self.service.id,
            'booking_date': self.target_date.strftime('%Y-%m-%d'),
            'booking_time': '04:30 PM',
            'venue_type': 'studio',
            'customer_name': 'Aarohi Patel',
            'customer_email': 'aarohi@example.com',
            'customer_phone': '+91 98111 22233',
            'special_notes': 'Peacock motifs please'
        }
        response = self.client.post(reverse('booking'), post_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify created in DB
        booking = Booking.objects.get(customer_email='aarohi@example.com')
        self.assertEqual(booking.booking_time, '04:30 PM')
        self.assertTrue(booking.booking_ref.startswith('MH-'))

    def test_pages_render_cleanly(self):
        """Test all public pages return HTTP 200"""
        for url_name in ['home', 'about', 'services', 'gallery', 'booking', 'login', 'register']:
            res = self.client.get(reverse(url_name))
            self.assertEqual(res.status_code, 200, f"Page {url_name} failed to render")

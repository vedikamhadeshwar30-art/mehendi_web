import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class BusinessSettings(models.Model):
    """Singleton model for studio business configuration."""
    business_name = models.CharField(max_length=150, default='Aura Mehendi Artistry')
    tagline = models.CharField(max_length=200, default='Haute Henna Atelier')
    phone = models.CharField(max_length=25, default='+91 98765 43210')
    email = models.EmailField(default='bookings@auramehendi.com')
    whatsapp = models.CharField(max_length=25, default='+919876543210')
    instagram = models.CharField(max_length=120, default='@auramehendi')
    address = models.TextField(default='Bandra West, Mumbai, Maharashtra 400050')
    about = models.TextField(default='Exquisite bridal and contemporary henna artistry using 100% organic Rajasthani henna.')
    mon_fri_hours = models.CharField(max_length=50, default='09:00 AM – 09:30 PM')
    sat_hours = models.CharField(max_length=50, default='09:00 AM – 09:30 PM')
    sun_hours = models.CharField(max_length=50, default='10:00 AM – 07:00 PM')

    class Meta:
        verbose_name = 'Business Settings'

    def __str__(self):
        return self.business_name

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Service(models.Model):
    CATEGORY_CHOICES = [
        ('bridal', 'Bridal Couture'),
        ('arabic', 'Arabic & Floral'),
        ('indo_western', 'Indo-Western & Fusion'),
        ('mandala', 'Mandala & Minimalist'),
        ('party', 'Sangeet & Party Mehendi'),
        ('traditional', 'Traditional Rajasthani/Marwari'),
    ]

    title = models.CharField(max_length=120)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='bridal')
    tagline = models.CharField(max_length=200, blank=True, help_text="Short highlight, e.g., 'Elaborate elbow-length bridal intricacy'")
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=2.0)
    badge = models.CharField(max_length=50, blank=True, help_text="e.g. 'Most Popular', 'Bridal Signature'")
    image_url = models.CharField(max_length=400, blank=True, help_text="Image URL or static path")
    image = models.ImageField(upload_to='services/', null=True, blank=True, help_text="Upload image (overrides image URL)")
    features_list = models.TextField(blank=True, help_text="Enter features separated by commas or newlines")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, help_text="Inactive services won't appear on the public site")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', 'price']

    def __str__(self):
        return f"{self.title} (₹{self.price})"

    def get_features(self):
        if not self.features_list:
            return []
        lines = [f.strip() for f in self.features_list.replace('\r\n', '\n').split('\n') if f.strip()]
        if len(lines) == 1 and ',' in lines[0]:
            return [item.strip() for item in lines[0].split(',') if item.strip()]
        return lines


class GalleryItem(models.Model):
    CATEGORY_CHOICES = [
        ('bridal', 'Bridal Couture'),
        ('arabic', 'Arabic & Floral'),
        ('indo_western', 'Indo-Western'),
        ('mandala', 'Mandala Art'),
        ('feet', 'Feet & Bridal Leg Art'),
        ('minimal', 'Minimalist & Finger'),
    ]

    title = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='bridal')
    image_url = models.CharField(max_length=400, blank=True)
    image = models.ImageField(upload_to='gallery/', null=True, blank=True, help_text="Upload design image")
    description = models.TextField(blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="e.g. Dark Stain, Eucalyptus Oil, Sangeet")
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_image(self):
        """Returns the best available image source."""
        if self.image:
            return self.image.url
        return self.image_url

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('REJECTED', 'Rejected'),
    ]

    VENUE_CHOICES = [
        ('studio', 'Artist Luxury Studio (In-Salon)'),
        ('home', 'Client Venue / Home Visit (+ ₹500 Travel)'),
    ]

    TIME_SLOTS = [
        ('09:00 AM', '09:00 AM - 11:30 AM (Morning Slot)'),
        ('11:30 AM', '11:30 AM - 02:00 PM (Mid-Day Slot)'),
        ('02:00 PM', '02:00 PM - 04:30 PM (Afternoon Slot)'),
        ('04:30 PM', '04:30 PM - 07:00 PM (Evening Sunset Slot)'),
        ('07:00 PM', '07:00 PM - 09:30 PM (Night Gala Slot)'),
    ]

    booking_ref = models.CharField(max_length=20, unique=True, editable=False, db_index=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    booking_date = models.DateField()
    booking_time = models.CharField(max_length=20, choices=TIME_SLOTS)
    venue_type = models.CharField(max_length=20, choices=VENUE_CHOICES, default='studio')
    address = models.TextField(blank=True, help_text="Full address for Home / Wedding Venue visit")
    special_notes = models.TextField(blank=True, help_text="Custom bridal figures, special requests, number of hands, etc.")
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-booking_date', '-booking_time']
        constraints = [
            models.UniqueConstraint(
                fields=['booking_date', 'booking_time'],
                condition=~models.Q(status='CANCELLED'),
                name='unique_active_slot_booking'
            )
        ]

    def __str__(self):
        return f"{self.booking_ref} - {self.customer_name} ({self.booking_date} @ {self.booking_time})"

    def clean(self):
        super().clean()
        if self.booking_date and self.booking_date < timezone.now().date():
            raise ValidationError({'booking_date': 'Booking date cannot be in the past.'})

        conflict_query = Booking.objects.filter(
            booking_date=self.booking_date,
            booking_time=self.booking_time
        ).exclude(status='CANCELLED')

        if self.pk:
            conflict_query = conflict_query.exclude(pk=self.pk)

        if conflict_query.exists():
            raise ValidationError({
                'booking_time': f"The time slot '{self.booking_time}' on {self.booking_date} is already booked. Please choose another available slot."
            })

    def save(self, *args, **kwargs):
        if not self.booking_ref:
            self.booking_ref = f"MH-{uuid.uuid4().hex[:6].upper()}"

        if self.service and not self.total_price:
            base_price = self.service.price
            if self.venue_type == 'home':
                base_price += 500
            self.total_price = base_price

        self.full_clean()
        super().save(*args, **kwargs)


class Review(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviews')
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL, related_name='review')
    client_name = models.CharField(max_length=120)
    client_location = models.CharField(max_length=120, default='Mumbai, Maharashtra')
    service_taken = models.ForeignKey(Service, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviews')
    rating = models.PositiveSmallIntegerField(default=5, choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client_name} - {self.rating} star"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('new_booking', 'New Booking'),
        ('cancellation', 'Booking Cancelled'),
        ('review', 'New Review'),
        ('reschedule', 'Booking Rescheduled'),
        ('status_change', 'Status Changed'),
    ]

    notif_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='new_booking')
    booking = models.ForeignKey('Booking', null=True, blank=True, on_delete=models.SET_NULL, related_name='notifications')
    review = models.ForeignKey('Review', null=True, blank=True, on_delete=models.SET_NULL, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notif_type_display()}: {self.title}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Fully Paid'),
    ]

    booking = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='payment')
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    advance_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UNPAID')
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Payment for {self.booking.booking_ref} - {self.get_payment_status_display()}"

    @property
    def remaining_amount(self):
        return self.total_amount - self.advance_paid

    def save(self, *args, **kwargs):
        # Auto-update status based on amounts
        if self.advance_paid >= self.total_amount:
            self.payment_status = 'PAID'
        elif self.advance_paid > 0:
            self.payment_status = 'PARTIAL'
        else:
            self.payment_status = 'UNPAID'
        super().save(*args, **kwargs)


class TimeSlotBlock(models.Model):
    """Admin-controlled slot blocking for unavailability management."""
    date = models.DateField()
    time_slot = models.CharField(max_length=20)
    is_blocked = models.BooleanField(default=True)
    reason = models.CharField(max_length=200, blank=True, default='Artist Unavailable')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('date', 'time_slot')]
        ordering = ['date', 'time_slot']

    def __str__(self):
        return f"BLOCKED: {self.date} @ {self.time_slot} ({self.reason})"

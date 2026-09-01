"""
Django signals for auto-generating Notifications and Payments
when Bookings and Reviews are created or updated.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking, Review, Notification, Payment


@receiver(post_save, sender=Booking)
def handle_booking_notifications(sender, instance, created, **kwargs):
    """
    Create notifications for admin when:
    - A new booking is made (new_booking)
    - A booking is cancelled (cancellation)
    - A booking status changes (status_change)
    Also auto-create a Payment record on new booking.
    """
    if created:
        # New booking notification
        Notification.objects.create(
            notif_type='new_booking',
            booking=instance,
            title=f'New booking from {instance.customer_name}',
            message=(
                f'{instance.service.title} — '
                f'{instance.booking_date.strftime("%d %b %Y")}, '
                f'{instance.booking_time}\n'
                f'Ref: #{instance.booking_ref} | '
                f'Contact: {instance.customer_phone}'
            )
        )
        # Auto-create Payment record
        Payment.objects.get_or_create(
            booking=instance,
            defaults={'total_amount': instance.total_price, 'advance_paid': 0}
        )
    else:
        # Detect cancellation or rejection
        if instance.status in ('CANCELLED', 'REJECTED'):
            # Avoid duplicate notifications on repeated saves
            already = Notification.objects.filter(
                booking=instance,
                notif_type='cancellation'
            ).exists()
            if not already:
                Notification.objects.create(
                    notif_type='cancellation',
                    booking=instance,
                    title=f'Booking {instance.status.lower()} — #{instance.booking_ref}',
                    message=(
                        f'{instance.customer_name} | '
                        f'{instance.service.title} on '
                        f'{instance.booking_date.strftime("%d %b %Y")} @ '
                        f'{instance.booking_time}'
                    )
                )


@receiver(post_save, sender=Review)
def handle_review_notification(sender, instance, created, **kwargs):
    """Create a notification when a new review is submitted."""
    if created:
        Notification.objects.create(
            notif_type='review',
            review=instance,
            title=f'New review from {instance.client_name}',
            message=(
                f'{instance.rating}/5 stars — '
                f'"{instance.comment[:100]}..."'
                if len(instance.comment) > 100
                else f'{instance.rating}/5 stars — "{instance.comment}"'
            )
        )

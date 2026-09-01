from django.contrib import admin
from .models import Service, GalleryItem, Booking, Review


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'duration_hours', 'badge', 'is_featured', 'created_at')
    list_filter = ('category', 'is_featured')
    search_fields = ('title', 'description', 'badge')
    list_editable = ('price', 'is_featured')


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_featured', 'created_at')
    list_filter = ('category', 'is_featured')
    search_fields = ('title', 'description', 'tags')
    list_editable = ('is_featured',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_ref', 'customer_name', 'service', 'booking_date', 'booking_time', 'venue_type', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'venue_type', 'booking_date', 'service')
    search_fields = ('booking_ref', 'customer_name', 'customer_email', 'customer_phone', 'address')
    list_editable = ('status',)
    date_hierarchy = 'booking_date'
    readonly_fields = ('booking_ref', 'created_at', 'updated_at')
    actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled']

    def mark_confirmed(self, request, queryset):
        queryset.update(status='CONFIRMED')
    mark_confirmed.short_description = "Mark selected bookings as Confirmed"

    def mark_completed(self, request, queryset):
        queryset.update(status='COMPLETED')
    mark_completed.short_description = "Mark selected bookings as Completed"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='CANCELLED')
    mark_cancelled.short_description = "Mark selected bookings as Cancelled"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_location', 'rating', 'service_taken', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('client_name', 'comment', 'client_location')
    list_editable = ('is_approved',)

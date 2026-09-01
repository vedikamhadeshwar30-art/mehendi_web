from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime

from .models import Service, GalleryItem, Booking, Review, TimeSlotBlock
from .forms import BookingForm, ReviewForm, CustomUserRegistrationForm, CustomUserLoginForm


def home(request):
    featured_services = Service.objects.filter(is_featured=True)[:4]
    if not featured_services.exists():
        featured_services = Service.objects.all()[:4]
    
    gallery_preview = GalleryItem.objects.all()[:6]
    reviews = Review.objects.filter(is_approved=True)[:6]
    review_form = ReviewForm()

    context = {
        'featured_services': featured_services,
        'gallery_preview': gallery_preview,
        'reviews': reviews,
        'review_form': review_form,
    }
    return render(request, 'booking/home.html', context)


def about(request):
    reviews_count = Review.objects.count()
    context = {
        'reviews_count': reviews_count,
    }
    return render(request, 'booking/about.html', context)


def services(request):
    category_filter = request.GET.get('category', 'all')
    if category_filter and category_filter != 'all':
        services_list = Service.objects.filter(category=category_filter)
    else:
        services_list = Service.objects.all()

    categories = Service.CATEGORY_CHOICES
    context = {
        'services': services_list,
        'categories': categories,
        'active_category': category_filter,
    }
    return render(request, 'booking/services.html', context)


def gallery(request):
    category_filter = request.GET.get('category', 'all')
    if category_filter and category_filter != 'all':
        items = GalleryItem.objects.filter(category=category_filter)
    else:
        items = GalleryItem.objects.all()

    categories = GalleryItem.CATEGORY_CHOICES
    context = {
        'gallery_items': items,
        'categories': categories,
        'active_category': category_filter,
    }
    return render(request, 'booking/gallery.html', context)


def booking_view(request):
    selected_service_id = request.GET.get('service')
    services = Service.objects.all()

    initial_data = {}
    if selected_service_id:
        try:
            initial_data['service'] = Service.objects.get(pk=selected_service_id)
        except (Service.DoesNotExist, ValueError):
            pass

    if request.user.is_authenticated:
        initial_data['customer_name'] = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        initial_data['customer_email'] = request.user.email

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            if request.user.is_authenticated:
                booking.user = request.user
            
            # Recalculate price with venue options
            base_price = booking.service.price
            if booking.venue_type == 'home':
                base_price += 500
            booking.total_price = base_price
            
            try:
                booking.save()
                messages.success(request, f"🎉 Booking Confirmed! Your booking reference is {booking.booking_ref}.")
                return redirect('booking_success', ref=booking.booking_ref)
            except Exception as e:
                messages.error(request, f"Could not complete booking: {e}")
        else:
            messages.error(request, "Please correct the errors in the booking form.")
    else:
        form = BookingForm(initial=initial_data)

    context = {
        'form': form,
        'services': services,
        'selected_service_id': selected_service_id,
        'today': timezone.now().strftime('%Y-%m-%d'),
        'time_slots': Booking.TIME_SLOTS,
    }
    return render(request, 'booking/booking.html', context)


def booking_success(request, ref):
    booking = get_object_or_404(Booking, booking_ref=ref)
    context = {
        'booking': booking,
    }
    return render(request, 'booking/booking_success.html', context)


def api_available_slots(request):
    """
    Returns JSON of available vs booked slots for a chosen date.
    A slot is unavailable if:
      1. A non-cancelled booking already exists for it, OR
      2. Admin has manually blocked it via TimeSlotBlock
    """
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date parameter is required'}, status=400)

    try:
        query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

    # Find booked slots on that date
    booked_slots = set(Booking.objects.filter(
        booking_date=query_date
    ).exclude(status__in=['CANCELLED', 'REJECTED']).values_list('booking_time', flat=True))

    # Find admin-blocked slots
    blocked_slots = set(TimeSlotBlock.objects.filter(
        date=query_date,
        is_blocked=True
    ).values_list('time_slot', flat=True))

    slots_data = []
    for slot_val, slot_label in Booking.TIME_SLOTS:
        is_booked = slot_val in booked_slots
        is_blocked = slot_val in blocked_slots
        is_available = not is_booked and not is_blocked
        reason = None
        if is_booked:
            reason = 'Booked'
        elif is_blocked:
            reason = 'Unavailable'
        slots_data.append({
            'value': slot_val,
            'label': slot_label,
            'is_available': is_available,
            'reason': reason
        })

    return JsonResponse({
        'date': date_str,
        'slots': slots_data,
        'booked_count': len(booked_slots),
        'blocked_count': len(blocked_slots),
        'total_slots': len(Booking.TIME_SLOTS)
    })



@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date', '-booking_time')
    context = {
        'bookings': bookings,
    }
    return render(request, 'booking/my_bookings.html', context)


@login_required
def cancel_booking(request, ref):
    booking = get_object_or_404(Booking, booking_ref=ref, user=request.user)
    if request.method == 'POST':
        if booking.status != 'COMPLETED':
            booking.status = 'CANCELLED'
            booking.save()
            messages.success(request, f"Booking #{booking.booking_ref} has been cancelled.")
        else:
            messages.warning(request, "Completed bookings cannot be cancelled.")
    return redirect('my_bookings')


def submit_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            if request.user.is_authenticated:
                review.user = request.user
            review.save()
            messages.success(request, "Thank you for your lovely review! It has been published.")
        else:
            messages.error(request, "Unable to submit review. Please ensure all required fields are filled.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def register_view(request):
    if request.user.is_authenticated:
        return redirect('my_bookings')

    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Mehendi Artistry, {user.first_name or user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Please resolve the errors below to complete registration.")
    else:
        form = CustomUserRegistrationForm()

    return render(request, 'booking/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('my_bookings')

    if request.method == 'POST':
        form = CustomUserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next', 'my_bookings')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = CustomUserLoginForm()

    return render(request, 'booking/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been safely logged out.")
    return redirect('home')

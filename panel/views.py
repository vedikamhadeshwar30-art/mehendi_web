"""
Custom Admin Panel views for Aura Mehendi Artistry.
All views require is_staff=True (staff_member_required decorator).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta, date
import json

from booking.models import (
    Booking, Service, GalleryItem, Review, Notification,
    Payment, TimeSlotBlock, BusinessSettings
)


# ─── helpers ────────────────────────────────────────────────────────────────

def _get_unread_count():
    return Notification.objects.filter(is_read=False).count()


# ─── Dashboard ──────────────────────────────────────────────────────────────

@staff_member_required(login_url='/login/')
def dashboard(request):
    today = timezone.now().date()
    qs = Booking.objects.all()

    stats = {
        'total_bookings': qs.count(),
        'pending': qs.filter(status='PENDING').count(),
        'confirmed': qs.filter(status='CONFIRMED').count(),
        'today': qs.filter(booking_date=today).count(),
        'completed': qs.filter(status='COMPLETED').count(),
        'cancelled': qs.filter(status__in=['CANCELLED', 'REJECTED']).count(),
        'total_customers': User.objects.filter(is_staff=False).count(),
        'total_revenue': Payment.objects.filter(
            booking__status='COMPLETED'
        ).aggregate(t=Sum('total_amount'))['t'] or 0,
        'advance_collected': Payment.objects.aggregate(
            t=Sum('advance_paid')
        )['t'] or 0,
    }

    recent_bookings = qs.select_related('service').order_by('-created_at')[:8]
    notifications = Notification.objects.filter(is_read=False)[:5]
    unread_count = _get_unread_count()

    # Chart data: bookings per day for last 7 days
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        chart_labels.append(d.strftime('%d %b'))
        chart_data.append(qs.filter(booking_date=d).count())

    # Revenue chart: last 6 months
    rev_labels = []
    rev_data = []
    for i in range(5, -1, -1):
        m_start = (today.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
        if m_start.month == 12:
            m_end = m_start.replace(year=m_start.year + 1, month=1, day=1)
        else:
            m_end = m_start.replace(month=m_start.month + 1, day=1)
        rev = Payment.objects.filter(
            booking__booking_date__gte=m_start,
            booking__booking_date__lt=m_end,
            booking__status='COMPLETED'
        ).aggregate(t=Sum('total_amount'))['t'] or 0
        rev_labels.append(m_start.strftime('%b %Y'))
        rev_data.append(float(rev))

    return render(request, 'panel/dashboard.html', {
        'stats': stats,
        'recent_bookings': recent_bookings,
        'notifications': notifications,
        'unread_count': unread_count,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'rev_labels': json.dumps(rev_labels),
        'rev_data': json.dumps(rev_data),
    })


# ─── Notifications ───────────────────────────────────────────────────────────

@staff_member_required(login_url='/login/')
def notifications(request):
    notifs = Notification.objects.all().select_related('booking', 'review')
    unread_count = notifs.filter(is_read=False).count()
    return render(request, 'panel/notifications.html', {
        'notifications': notifs,
        'unread_count': unread_count,
    })


@staff_member_required(login_url='/login/')
def mark_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
    return redirect('panel:notifications')


@staff_member_required(login_url='/login/')
def notification_detail_redirect(request, pk):
    """Mark a single notification read and redirect to its booking."""
    notif = get_object_or_404(Notification, pk=pk)
    notif.is_read = True
    notif.save()
    if notif.booking:
        return redirect('panel:booking_detail', pk=notif.booking.pk)
    return redirect('panel:notifications')


# ─── Bookings ────────────────────────────────────────────────────────────────

@staff_member_required(login_url='/login/')
def bookings_list(request):
    qs = Booking.objects.select_related('service', 'user').all()

    # Filters
    status_filter = request.GET.get('status', '')
    service_filter = request.GET.get('service', '')
    date_filter = request.GET.get('date', '')
    search_q = request.GET.get('q', '')

    if status_filter:
        qs = qs.filter(status=status_filter)
    if service_filter:
        qs = qs.filter(service_id=service_filter)
    if date_filter:
        qs = qs.filter(booking_date=date_filter)
    if search_q:
        qs = qs.filter(
            Q(customer_name__icontains=search_q) |
            Q(customer_email__icontains=search_q) |
            Q(customer_phone__icontains=search_q) |
            Q(booking_ref__icontains=search_q)
        )

    return render(request, 'panel/bookings/list.html', {
        'bookings': qs,
        'services': Service.objects.all(),
        'status_choices': Booking.STATUS_CHOICES,
        'status_filter': status_filter,
        'service_filter': service_filter,
        'date_filter': date_filter,
        'search_q': search_q,
        'unread_count': _get_unread_count(),
    })


@staff_member_required(login_url='/login/')
def booking_detail(request, pk):
    booking = get_object_or_404(Booking.objects.select_related('service', 'user'), pk=pk)

    # Get or create payment
    payment, _ = Payment.objects.get_or_create(
        booking=booking,
        defaults={'total_amount': booking.total_price}
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_status':
            new_status = request.POST.get('status')
            if new_status in dict(Booking.STATUS_CHOICES):
                old_status = booking.status
                booking.status = new_status
                # Skip model's full_clean to allow admin overrides on past dates
                Booking.objects.filter(pk=booking.pk).update(status=new_status)
                messages.success(request, f'Booking status updated to {new_status}.')
                return redirect('panel:booking_detail', pk=pk)

        elif action == 'update_payment':
            try:
                advance = float(request.POST.get('advance_paid', 0))
                notes = request.POST.get('notes', '')
                payment.advance_paid = advance
                payment.notes = notes
                payment.save()
                messages.success(request, 'Payment record updated.')
            except (ValueError, TypeError):
                messages.error(request, 'Invalid payment amount.')
            return redirect('panel:booking_detail', pk=pk)

    return render(request, 'panel/bookings/detail.html', {
        'booking': booking,
        'payment': payment,
        'status_choices': Booking.STATUS_CHOICES,
        'unread_count': _get_unread_count(),
        'rows': [
            ('Ref #', f'#{booking.booking_ref}'),
            ('Customer Name', booking.customer_name),
            ('Email', booking.customer_email),
            ('Phone', booking.customer_phone),
            ('Service', booking.service.title),
            ('Date', booking.booking_date.strftime('%A, %B %d, %Y')),
            ('Time Slot', booking.booking_time),
            ('Duration', f'{booking.service.duration_hours} Hours'),
            ('Venue', booking.get_venue_type_display()),
            ('Total Price', f'₹{booking.total_price:,.0f}'),
            ('Registered User', booking.user.username if booking.user else 'Guest Booking'),
            ('Booked On', booking.created_at.strftime('%b %d, %Y — %I:%M %p')),
        ]
    })


# ─── Customers ────────────────────────────────────────────────────────────────

@staff_member_required(login_url='/login/')
def customers_list(request):
    search_q = request.GET.get('q', '')
    qs = User.objects.filter(is_staff=False).annotate(
        booking_count=Count('bookings')
    )
    if search_q:
        qs = qs.filter(
            Q(username__icontains=search_q) |
            Q(first_name__icontains=search_q) |
            Q(last_name__icontains=search_q) |
            Q(email__icontains=search_q)
        )
    return render(request, 'panel/customers/list.html', {
        'customers': qs,
        'search_q': search_q,
        'unread_count': _get_unread_count(),
    })


@staff_member_required(login_url='/login/')
def customer_detail(request, pk):
    customer = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_active':
            customer.is_active = not customer.is_active
            customer.save()
            state = 'enabled' if customer.is_active else 'disabled'
            messages.success(request, f'Account {state} for {customer.username}.')
            return redirect('panel:customer_detail', pk=pk)

    bookings = Booking.objects.filter(user=customer).select_related('service')
    reviews = Review.objects.filter(user=customer).select_related('service_taken')
    return render(request, 'panel/customers/detail.html', {
        'customer': customer,
        'bookings': bookings,
        'reviews': reviews,
        'unread_count': _get_unread_count(),
    })


# ─── Services ─────────────────────────────────────────────────────────────────

@staff_member_required(login_url='/login/')
def services_list(request):
    services = Service.objects.all()
    return render(request, 'panel/services/list.html', {
        'services': services,
        'unread_count': _get_unread_count(),
    })


@staff_member_required(login_url='/login/')
def service_form(request, pk=None):
    service = get_object_or_404(Service, pk=pk) if pk else None
    category_choices = Service.CATEGORY_CHOICES

    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        title = data.get('title', '').strip()
        if not title:
            messages.error(request, 'Title is required.')
            return render(request, 'panel/services/form.html', {
                'service': service, 'category_choices': category_choices,
                'unread_count': _get_unread_count(),
            })

        fields = {
            'title': title,
            'category': data.get('category', 'bridal'),
            'tagline': data.get('tagline', ''),
            'description': data.get('description', ''),
            'price': float(data.get('price', 0)),
            'duration_hours': float(data.get('duration_hours', 2.0)),
            'badge': data.get('badge', ''),
            'image_url': data.get('image_url', ''),
            'features_list': data.get('features_list', ''),
            'is_featured': 'is_featured' in data,
            'is_active': 'is_active' in data,
        }

        if service:
            for k, v in fields.items():
                setattr(service, k, v)
            if 'image' in files:
                service.image = files['image']
            service.save()
            messages.success(request, f'Service "{service.title}" updated.')
        else:
            service = Service(**fields)
            if 'image' in files:
                service.image = files['image']
            service.save()
            messages.success(request, f'Service "{service.title}" created.')

        return redirect('panel:services_list')

    return render(request, 'panel/services/form.html', {
        'service': service,
        'category_choices': category_choices,
        'unread_count': _get_unread_count(),
    })


@staff_member_required(login_url='/login/')
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        name = service.title
        service.delete()
        messages.success(request, f'Service "{name}" deleted.')
    return redirect('panel:services_list')


@staff_member_required(login_url='/login/')
def service_toggle(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.is_active = not service.is_active
        service.save()
        state = 'activated' if service.is_active else 'deactivated'
        messages.success(request, f'Service "{service.title}" {state}.')
    return redirect('panel:services_list')


# ─── Gallery ──────────────────────────────────────────────────────────────────

@staff_member_required(login_url='/login/')
def gallery_list(request):
    items = GalleryItem.objects.all()
    return render(request, 'panel/gallery/list.html', {
        'items': items,
        'unread_count': _get_unread_count(),
    })


@staff_member_required(login_url='/login/')
def gallery_form(request, pk=None):
    item = get_object_or_404(GalleryItem, pk=pk) if pk else None
    category_choices = GalleryItem.CATEGORY_CHOICES

    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        title = data.get('title', '').strip()
        if not title:
            messages.error(request, 'Title is required.')
            return render(request, 'panel/gallery/form.html', {
                'item': item, 'category_choices': category_choices,
                'unread_count': _get_unread_count(),
            })

        fields = {
            'title': title,
            'category': data.get('category', 'bridal'),
            'image_url': data.get('image_url', ''),
            'description': data.get('description', ''),
            'tags': data.get('tags', ''),
            'is_featured': 'is_featured' in data,
        }

        if item:
            for k, v in fields.items():
                setattr(item, k, v)
            if 'image' in files:
                item.image = files['image']
            item.save()
            messages.success(request, f'Gallery item "{item.title}" updated.')
        else:
            item = GalleryItem(**fields)
            if 'image' in files:
                item.image = files['image']
            item.save()
            messages.success(request, f'Gallery item "{item.title}" uploaded.')

        return redirect('panel:gallery_list')

    return render(request, 'panel/gallery/form.html', {
        'item': item,
        'category_choices': category_choices,
        'unread_count': _get_unread_count(),
    })


@staff_member_required(login_url='/login/')
def gallery_delete(request, pk):
    item = get_object_or_404(GalleryItem, pk=pk)
    if request.method == 'POST':
        name = item.title
        item.delete()
        messages.success(request, f'Gallery item "{name}" deleted.')
    return redirect('panel:gallery_list')


# ─── Availability ─────────────────────────────────────────────────────────────

@staff_member_required(login_url='/login/')
def availability_manage(request):
    # Default: show next 7 days
    today = timezone.now().date()
    date_str = request.GET.get('date', today.strftime('%Y-%m-%d'))
    try:
        view_date = date.fromisoformat(date_str)
    except ValueError:
        view_date = today

    if request.method == 'POST':
        action = request.POST.get('action')
        slot_date = request.POST.get('date')
        slot_time = request.POST.get('time_slot')
        reason = request.POST.get('reason', 'Artist Unavailable')

        if action == 'block':
            obj, _ = TimeSlotBlock.objects.get_or_create(
                date=slot_date, time_slot=slot_time,
                defaults={'reason': reason, 'is_blocked': True}
            )
            obj.is_blocked = True
            obj.reason = reason
            obj.save()
            messages.success(request, f'Slot {slot_time} on {slot_date} blocked.')

        elif action == 'unblock':
            TimeSlotBlock.objects.filter(date=slot_date, time_slot=slot_time).delete()
            messages.success(request, f'Slot {slot_time} on {slot_date} unblocked.')

        return redirect(f'/admin-panel/availability/?date={slot_date}')

    # Build slot grid for date
    slots = Booking.TIME_SLOTS
    booked_times = set(Booking.objects.filter(
        booking_date=view_date
    ).exclude(status__in=['CANCELLED', 'REJECTED']).values_list('booking_time', flat=True))
    blocked_times = {
        b.time_slot: b.reason
        for b in TimeSlotBlock.objects.filter(date=view_date, is_blocked=True)
    }

    slot_grid = []
    for slot_val, slot_label in slots:
        is_booked = slot_val in booked_times
        is_blocked = slot_val in blocked_times
        booking_obj = None
        if is_booked:
            booking_obj = Booking.objects.filter(
                booking_date=view_date, booking_time=slot_val
            ).exclude(status__in=['CANCELLED', 'REJECTED']).select_related('service').first()

        slot_grid.append({
            'value': slot_val,
            'label': slot_label,
            'is_booked': is_booked,
            'is_blocked': is_blocked,
            'booking': booking_obj,
            'block_reason': blocked_times.get(slot_val, ''),
        })

    # Generate 14-day calendar for navigation
    calendar_days = [today + timedelta(days=i) for i in range(14)]

    return render(request, 'panel/availability/manage.html', {
        'view_date': view_date,
        'slot_grid': slot_grid,
        'calendar_days': calendar_days,
        'unread_count': _get_unread_count(),
    })


# ─── Reviews ──────────────────────────────────────────────────────────────────

@staff_member_required(login_url='/login/')
def reviews_list(request):
    filter_type = request.GET.get('filter', 'all')
    qs = Review.objects.select_related('service_taken', 'user').all()
    if filter_type == 'pending':
        qs = qs.filter(is_approved=False)
    elif filter_type == 'approved':
        qs = qs.filter(is_approved=True)

    return render(request, 'panel/reviews/list.html', {
        'reviews': qs,
        'filter_type': filter_type,
        'unread_count': _get_unread_count(),
    })


@staff_member_required(login_url='/login/')
def review_approve(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.is_approved = not review.is_approved
        review.save()
        state = 'approved' if review.is_approved else 'unapproved'
        messages.success(request, f'Review by {review.client_name} {state}.')
    return redirect('panel:reviews_list')


@staff_member_required(login_url='/login/')
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        name = review.client_name
        review.delete()
        messages.success(request, f'Review by {name} deleted.')
    return redirect('panel:reviews_list')


# ─── Payments ─────────────────────────────────────────────────────────────────

@staff_member_required(login_url='/login/')
def payments_list(request):
    status_filter = request.GET.get('status', '')
    qs = Payment.objects.select_related('booking', 'booking__service').all()
    if status_filter:
        qs = qs.filter(payment_status=status_filter)

    total_revenue = qs.filter(payment_status='PAID').aggregate(
        t=Sum('total_amount'))['t'] or 0
    total_advance = qs.aggregate(t=Sum('advance_paid'))['t'] or 0

    return render(request, 'panel/payments/list.html', {
        'payments': qs,
        'status_filter': status_filter,
        'payment_statuses': Payment.STATUS_CHOICES,
        'total_revenue': total_revenue,
        'total_advance': total_advance,
        'unread_count': _get_unread_count(),
    })


@staff_member_required(login_url='/login/')
def payment_detail(request, pk):
    payment = get_object_or_404(Payment.objects.select_related(
        'booking', 'booking__service'), pk=pk)

    if request.method == 'POST':
        try:
            advance = float(request.POST.get('advance_paid', payment.advance_paid))
            notes = request.POST.get('notes', payment.notes)
            payment.advance_paid = advance
            payment.notes = notes
            payment.save()
            messages.success(request, 'Payment updated successfully.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount entered.')
        return redirect('panel:payment_detail', pk=pk)

    return render(request, 'panel/payments/detail.html', {
        'payment': payment,
        'unread_count': _get_unread_count(),
    })


# ─── Reports ──────────────────────────────────────────────────────────────────

@staff_member_required(login_url='/login/')
def reports_dashboard(request):
    today = timezone.now().date()
    qs = Booking.objects.all()

    # Daily: last 14 days
    daily_labels, daily_data = [], []
    for i in range(13, -1, -1):
        d = today - timedelta(days=i)
        daily_labels.append(d.strftime('%d %b'))
        daily_data.append(qs.filter(booking_date=d).count())

    # Monthly: last 6 months
    monthly_labels, monthly_data = [], []
    for i in range(5, -1, -1):
        m_start = (today.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
        if m_start.month == 12:
            m_end = m_start.replace(year=m_start.year + 1, month=1, day=1)
        else:
            m_end = m_start.replace(month=m_start.month + 1, day=1)
        monthly_labels.append(m_start.strftime('%b %Y'))
        monthly_data.append(qs.filter(
            booking_date__gte=m_start, booking_date__lt=m_end).count())

    # Revenue monthly
    revenue_data = []
    for i in range(5, -1, -1):
        m_start = (today.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
        if m_start.month == 12:
            m_end = m_start.replace(year=m_start.year + 1, month=1, day=1)
        else:
            m_end = m_start.replace(month=m_start.month + 1, day=1)
        rev = Payment.objects.filter(
            booking__booking_date__gte=m_start,
            booking__booking_date__lt=m_end,
            booking__status='COMPLETED'
        ).aggregate(t=Sum('total_amount'))['t'] or 0
        revenue_data.append(float(rev))

    # Status donut
    status_data = {
        'PENDING': qs.filter(status='PENDING').count(),
        'CONFIRMED': qs.filter(status='CONFIRMED').count(),
        'COMPLETED': qs.filter(status='COMPLETED').count(),
        'CANCELLED': qs.filter(status='CANCELLED').count(),
        'REJECTED': qs.filter(status='REJECTED').count(),
    }

    # Top services
    top_services = (
        Service.objects.annotate(bcount=Count('bookings'))
        .order_by('-bcount')[:5]
    )

    return render(request, 'panel/reports/dashboard.html', {
        'daily_labels': json.dumps(daily_labels),
        'daily_data': json.dumps(daily_data),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
        'revenue_data': json.dumps(revenue_data),
        'status_data': json.dumps(status_data),
        'top_services': top_services,
        'total_revenue': sum(revenue_data),
        'unread_count': _get_unread_count(),
    })


# ─── Settings ─────────────────────────────────────────────────────────────────

@staff_member_required(login_url='/login/')
def business_settings(request):
    settings_obj = BusinessSettings.get_settings()

    if request.method == 'POST':
        for field in [
            'business_name', 'tagline', 'phone', 'email',
            'whatsapp', 'instagram', 'address', 'about',
            'mon_fri_hours', 'sat_hours', 'sun_hours'
        ]:
            val = request.POST.get(field, '').strip()
            if val:
                setattr(settings_obj, field, val)
        settings_obj.save()
        messages.success(request, 'Business settings saved successfully.')
        return redirect('panel:business_settings')

    return render(request, 'panel/settings/form.html', {
        'settings': settings_obj,
        'unread_count': _get_unread_count(),
    })


@staff_member_required(login_url='/login/')
def admin_profile(request):
    if request.method == 'POST':
        old_pw = request.POST.get('old_password')
        new_pw1 = request.POST.get('new_password1')
        new_pw2 = request.POST.get('new_password2')

        if not request.user.check_password(old_pw):
            messages.error(request, 'Current password is incorrect.')
        elif new_pw1 != new_pw2:
            messages.error(request, 'New passwords do not match.')
        elif len(new_pw1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            request.user.set_password(new_pw1)
            request.user.save()
            messages.success(request, 'Password changed. Please log in again.')
            return redirect('/login/')

    return render(request, 'panel/settings/profile.html', {
        'unread_count': _get_unread_count(),
    })

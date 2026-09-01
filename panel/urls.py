from django.urls import path
from . import views

app_name = 'panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard_explicit'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('notifications/<int:pk>/', views.notification_detail_redirect, name='notification_detail'),

    # Bookings
    path('bookings/', views.bookings_list, name='bookings_list'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),

    # Customers
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),

    # Services
    path('services/', views.services_list, name='services_list'),
    path('services/add/', views.service_form, name='service_add'),
    path('services/<int:pk>/edit/', views.service_form, name='service_edit'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    path('services/<int:pk>/toggle/', views.service_toggle, name='service_toggle'),

    # Gallery
    path('gallery/', views.gallery_list, name='gallery_list'),
    path('gallery/upload/', views.gallery_form, name='gallery_upload'),
    path('gallery/<int:pk>/edit/', views.gallery_form, name='gallery_edit'),
    path('gallery/<int:pk>/delete/', views.gallery_delete, name='gallery_delete'),

    # Availability
    path('availability/', views.availability_manage, name='availability_manage'),

    # Reviews
    path('reviews/', views.reviews_list, name='reviews_list'),
    path('reviews/<int:pk>/approve/', views.review_approve, name='review_approve'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),

    # Payments
    path('payments/', views.payments_list, name='payments_list'),
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),

    # Reports
    path('reports/', views.reports_dashboard, name='reports_dashboard'),

    # Settings
    path('settings/', views.business_settings, name='business_settings'),
    path('profile/', views.admin_profile, name='admin_profile'),
]

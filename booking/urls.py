from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('gallery/', views.gallery, name='gallery'),
    path('book/', views.booking_view, name='booking'),
    path('book/success/<str:ref>/', views.booking_success, name='booking_success'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('my-bookings/cancel/<str:ref>/', views.cancel_booking, name='cancel_booking'),
    path('review/submit/', views.submit_review, name='submit_review'),
    path('api/available-slots/', views.api_available_slots, name='api_available_slots'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]

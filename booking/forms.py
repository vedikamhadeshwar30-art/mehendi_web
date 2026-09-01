from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from .models import Booking, Review, Service


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'service',
            'booking_date',
            'booking_time',
            'venue_type',
            'customer_name',
            'customer_email',
            'customer_phone',
            'address',
            'special_notes'
        ]
        widgets = {
            'service': forms.Select(attrs={'class': 'form-select', 'id': 'service-select'}),
            'booking_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'booking-date-input',
                'min': timezone.now().strftime('%Y-%m-%d')
            }),
            'booking_time': forms.Select(attrs={'class': 'form-select', 'id': 'time-slot-select'}),
            'venue_type': forms.Select(attrs={'class': 'form-select', 'id': 'venue-type-select'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Your Complete Venue Address (Required for Home Visit)'}),
            'special_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Bridal theme, number of family members, skin sensitivities, etc.'}),
        }

    def clean_booking_date(self):
        booking_date = self.cleaned_data.get('booking_date')
        if booking_date and booking_date < timezone.now().date():
            raise forms.ValidationError("Booking date cannot be in the past. Please select today or a future date.")
        return booking_date

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('booking_date')
        booking_time = cleaned_data.get('booking_time')
        venue_type = cleaned_data.get('venue_type')
        address = cleaned_data.get('address')

        if venue_type == 'home' and not address:
            self.add_error('address', 'Please provide a venue address for home visits.')

        if booking_date and booking_time:
            # Check for conflict
            conflict = Booking.objects.filter(
                booking_date=booking_date,
                booking_time=booking_time
            ).exclude(status='CANCELLED')

            if self.instance and self.instance.pk:
                conflict = conflict.exclude(pk=self.instance.pk)

            if conflict.exists():
                self.add_error('booking_time', f"The slot '{booking_time}' on {booking_date.strftime('%b %d, %Y')} is already booked. Please choose another time slot.")

        return cleaned_data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['client_name', 'client_location', 'service_taken', 'rating', 'comment']
        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'client_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, State (e.g. Mumbai)'}),
            'service_taken': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.HiddenInput(attrs={'id': 'rating-value-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share your experience with our henna artistry, stain depth, punctuality...'}),
        }


class CustomUserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


class CustomUserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})

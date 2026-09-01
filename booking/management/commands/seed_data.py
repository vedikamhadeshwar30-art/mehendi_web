from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from booking.models import (
    Service, GalleryItem, Booking, Review,
    Notification, Payment, BusinessSettings
)


class Command(BaseCommand):
    help = 'Populate database with rich mock services, gallery items, reviews, and test user'

    def handle(self, *args, **options):
        self.stdout.write("Seeding Mehendi Booking database...")

        # 1. Create Superuser / Admin if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@auramehendi.com', 'admin123')
            self.stdout.write(self.style.SUCCESS("[OK] Superuser created: admin / admin123"))

        # Create demo customer
        if not User.objects.filter(username='ananya').exists():
            user = User.objects.create_user('ananya', 'ananya@example.com', 'pass123', first_name='Ananya', last_name='Deshmukh')
            self.stdout.write(self.style.SUCCESS("[OK] Demo client created: ananya / pass123"))

        # 2. Populate Services
        Service.objects.all().delete()
        services_data = [
            {
                'title': 'The Royal Maharani Bridal Package',
                'category': 'bridal',
                'tagline': 'Bespoke elbow-length intricate bridal storytelling',
                'description': 'Our most coveted bespoke bridal experience. Covers full arms up to elbows (front and back) and feet up to mid-calf. Features personalized portraiture, wedding hashtags, sacred hastamelap motifs, and custom couple journey timelines.',
                'price': 15000.00,
                'duration_hours': 4.5,
                'badge': 'Signature Bridal',
                'image_url': 'https://images.unsplash.com/photo-1599839575945-a9e5af0c3fa5?auto=format&fit=crop&w=800&q=80',
                'features_list': 'Elbow-length arms (both sides)\nFeet till mid-calf\nCustom bride & groom portraits\nPersonalized wedding vows & dates\nComplimentary aftercare kit & sealant spray',
                'is_featured': True
            },
            {
                'title': 'Indo-Arabic Contemporary Fusion',
                'category': 'arabic',
                'tagline': 'Bold shaded floral jaals with modern negative spacing',
                'description': 'A stunning modern aesthetic featuring dramatic bold outlines, delicate micro-shading, and organic flow. Perfect for fashion-forward brides, engagement ceremonies, and cocktail nights.',
                'price': 7500.00,
                'duration_hours': 2.5,
                'badge': 'Most Popular',
                'image_url': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80',
                'features_list': 'Forearm length front and back\nBold shading & negative contouring\nFloral & leaf trail motifs\nFast-drying formula with eucalyptus oil',
                'is_featured': True
            },
            {
                'title': 'Traditional Marwari Heritage Bridal',
                'category': 'traditional',
                'tagline': 'Centuries-old Rajasthani jharokhas, peacocks & doli motifs',
                'description': 'Deeply rooted in Rajasthan’s royal court tradition. Features ultra-fine symmetric checks, dancing peacocks, traditional elephant processions, and intricate temple jaali patterns.',
                'price': 12500.00,
                'duration_hours': 3.5,
                'badge': 'Heritage Classic',
                'image_url': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=800&q=80',
                'features_list': 'Full arm symmetric jaali work\nDetailed bridal doli & elephant accents\nFeet till ankle adornment\nDeep mahogany stain guarantee',
                'is_featured': True
            },
            {
                'title': 'Minimalist Mandala & Lace Elegance',
                'category': 'mandala',
                'tagline': 'Sacred geometric mandalas with delicate finger cuffs',
                'description': 'Designed for the minimalist bride and bridesmaid. Centered around mesmerizing lotus and geometry mandalas on the palms, accented by lace jewelry glove styling on the fingers.',
                'price': 4500.00,
                'duration_hours': 1.5,
                'badge': 'Minimal Chic',
                'image_url': 'https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=800&q=80',
                'features_list': 'Center palm sacred lotus mandala\nFine glove lace finger detailing\nBackhand matching mandala charm\nLightweight and quick drying',
                'is_featured': False
            },
            {
                'title': 'Sangeet & Family Guest Henna Lounge',
                'category': 'party',
                'tagline': 'Exquisite party designs for up to 10 bridesmaids & family',
                'description': 'High-speed yet immaculate artistic coverage for your closest family and friends. Includes full palm coverage for up to 10 guests with two artist cones running in harmony.',
                'price': 9000.00,
                'duration_hours': 3.0,
                'badge': 'Group Special',
                'image_url': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=800&q=80',
                'features_list': 'Up to 10 guest palms (front or back)\nCustomized quick-set designs\nAll natural organic cones included\nIdeal for Sangeet / Mehendi party lounge',
                'is_featured': False
            },
            {
                'title': 'Intimate Engagement & Roka Charm',
                'category': 'bridal',
                'tagline': 'Forearm delicate florals with entwined couple initials',
                'description': 'An elegant mid-coverage package crafted specifically for Roka, Engagement, and Sagan ceremonies. Features graceful floral bands and hidden initials.',
                'price': 6000.00,
                'duration_hours': 2.0,
                'badge': 'Bestseller',
                'image_url': 'https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=800&q=80',
                'features_list': 'Forearm length front and back\nHidden couple initials\nFloral and leaf symmetry\nComplimentary aftercare sealant',
                'is_featured': True
            }
        ]

        created_services = []
        for s_data in services_data:
            s = Service.objects.create(**s_data)
            created_services.append(s)
        self.stdout.write(self.style.SUCCESS(f"[OK] Created {len(created_services)} services"))

        # 3. Populate Gallery Items
        GalleryItem.objects.all().delete()
        gallery_data = [
            {
                'title': 'Royal Jharokha & Portrait Palms',
                'category': 'bridal',
                'image_url': 'https://images.unsplash.com/photo-1599839575945-a9e5af0c3fa5?auto=format&fit=crop&w=800&q=80',
                'description': 'Custom bride and groom portraits encased in Rajasthani arched windows.',
                'tags': 'Bridal, Portraits, Marwari, Dark Stain',
                'is_featured': True
            },
            {
                'title': 'Negative Space Arabic Rose Trail',
                'category': 'arabic',
                'image_url': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80',
                'description': 'Bold cascading floral vine with dramatic negative space highlights.',
                'tags': 'Arabic, Modern, Floral, Sangeet',
                'is_featured': True
            },
            {
                'title': 'Sacred Lotus Geometry Mandala',
                'category': 'mandala',
                'image_url': 'https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=800&q=80',
                'description': 'Pristine center mandala radiating lotus symmetry and lace finger rings.',
                'tags': 'Mandala, Lotus, Minimal, Engagement',
                'is_featured': True
            },
            {
                'title': 'Anklet & Paayal Bridal Leg Art',
                'category': 'feet',
                'image_url': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=800&q=80',
                'description': 'Intricate royal paayal lace bands and mirror checks extending up to mid-calf.',
                'tags': 'Feet Art, Bridal, Paayal, Rajasthani',
                'is_featured': True
            },
            {
                'title': 'Delicate French Lace & Finger Bands',
                'category': 'minimal',
                'image_url': 'https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=800&q=80',
                'description': 'Feather-light modern geometric lines and ring cuff accents.',
                'tags': 'Minimalist, Ring, Contemporary, Chic',
                'is_featured': True
            },
            {
                'title': 'The Grand Baarat Procession',
                'category': 'bridal',
                'image_url': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=800&q=80',
                'description': 'Storytelling bridal composition illustrating the baarat, doli, and shehnai players.',
                'tags': 'Heritage, Doli, Baarat, Royal Wedding',
                'is_featured': True
            }
        ]

        for g_data in gallery_data:
            GalleryItem.objects.create(**g_data)
        self.stdout.write(self.style.SUCCESS(f"[OK] Created {len(gallery_data)} gallery items"))

        # 4. Populate Reviews
        Review.objects.all().delete()
        reviews_data = [
            {
                'client_name': 'Ananya Deshmukh',
                'client_location': 'Bandra West, Mumbai',
                'service_taken': created_services[0],
                'rating': 5,
                'comment': 'Riya is a true magician! The precision in my bridal portrait and wedding vows was unbelievable. The stain developed into the most gorgeous deep burgundy by wedding day. Every guest couldn’t stop complimenting!',
                'is_approved': True
            },
            {
                'client_name': 'Priya & Kunal Mehta',
                'client_location': 'Juhu, Mumbai',
                'service_taken': created_services[1],
                'rating': 5,
                'comment': 'I chose the Indo-Arabic package for our engagement and it exceeded every expectation. The bold shaded roses looked like fine lace jewelry. Plus, pure eucalyptus fragrance with no chemical stinging at all.',
                'is_approved': True
            },
            {
                'client_name': 'Dr. Natasha Fernandes',
                'client_location': 'Goa Destination Wedding',
                'service_taken': created_services[4],
                'rating': 5,
                'comment': 'Booked the Sangeet Henna Lounge for my 12 bridesmaids. Riya was so fast, punctual, and patient with each girl’s custom preferences. She truly made our night unforgettable!',
                'is_approved': True
            },
            {
                'client_name': 'Simran Kaur',
                'client_location': 'South Mumbai',
                'service_taken': created_services[2],
                'rating': 5,
                'comment': 'Pure Rajasthani traditional heritage art at its finest! The dancing peacock jaals were so crisp and detailed. The 4-step aftercare guide worked wonders for my stain.',
                'is_approved': True
            }
        ]

        for r_data in reviews_data:
            Review.objects.create(**r_data)
        self.stdout.write(self.style.SUCCESS(f"[OK] Created {len(reviews_data)} client reviews"))

        # 5. Populate Sample Bookings to demonstrate slot availability
        Booking.objects.all().delete()
        tomorrow = timezone.now().date() + timedelta(days=1)

        sample_booking1 = Booking(
            service=created_services[0],
            customer_name='Tanvi Singhania',
            customer_email='tanvi.s@example.com',
            customer_phone='+91 98201 12345',
            booking_date=tomorrow,
            booking_time='09:00 AM',
            venue_type='studio',
            total_price=created_services[0].price,
            status='CONFIRMED'
        )
        sample_booking1.save()

        sample_booking2 = Booking(
            service=created_services[1],
            customer_name='Meera Kapadia',
            customer_email='meera.k@example.com',
            customer_phone='+91 98202 54321',
            booking_date=tomorrow,
            booking_time='02:00 PM',
            venue_type='home',
            address='Villa 4, Sea Face Towers, Worli, Mumbai',
            total_price=created_services[1].price + 500,
            status='CONFIRMED'
        )
        sample_booking2.save()

        self.stdout.write(self.style.SUCCESS(f"[OK] Created 2 sample active bookings (demonstrating blocked slots on {tomorrow})"))

        # 8. Ensure admin user is staff + superuser
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("[OK] Admin user confirmed as staff/superuser"))

        # 9. Seed BusinessSettings singleton
        bs = BusinessSettings.get_settings()
        bs.business_name = 'Aura Mehendi Artistry'
        bs.tagline = 'Haute Henna Atelier — Bespoke Bridal & Contemporary Designs'
        bs.phone = '+91 98765 43210'
        bs.email = 'bookings@auramehendi.com'
        bs.whatsapp = '+919876543210'
        bs.instagram = '@auramehendi'
        bs.address = 'Studio 12, The Creative Hub, Bandra West, Mumbai — 400050'
        bs.about = (
            'Aura Mehendi Artistry is Mumbai\'s premier luxury henna studio specialising in '
            'bespoke bridal and contemporary mehendi designs. We use 100% organic Rajasthani '
            'henna paste for the deepest, richest stains.'
        )
        bs.mon_fri_hours = '09:00 AM – 09:30 PM'
        bs.sat_hours = '09:00 AM – 09:30 PM'
        bs.sun_hours = '10:00 AM – 07:00 PM'
        bs.save()
        self.stdout.write(self.style.SUCCESS("[OK] BusinessSettings seeded"))

        # 10. Create Payment records for existing bookings that don't have one
        for booking_obj in Booking.objects.all():
            Payment.objects.get_or_create(
                booking=booking_obj,
                defaults={'total_amount': booking_obj.total_price, 'advance_paid': 0}
            )
        self.stdout.write(self.style.SUCCESS("[OK] Payment records ensured for all bookings"))

        # 11. Seed a few sample notifications if none exist
        if Notification.objects.count() == 0:
            all_bookings = list(Booking.objects.all()[:3])
            sample_notifs = [
                {
                    'notif_type': 'new_booking',
                    'title': 'New booking from Priya Sharma',
                    'message': 'Bridal Signature Mehendi — Tomorrow, 09:00 AM\nRef: #MH-DEMO1 | +91 98100 12345',
                    'booking': all_bookings[0] if all_bookings else None,
                },
                {
                    'notif_type': 'review',
                    'title': 'New 5-star review from Meera Joshi',
                    'message': '5/5 stars — "Absolutely stunning bridal mehendi! The stain was incredibly dark..."',
                },
                {
                    'notif_type': 'new_booking',
                    'title': 'New booking from Nisha Kapoor',
                    'message': 'Arabic Garden Pattern — 3 days from now, 02:00 PM\nRef: #MH-DEMO2',
                    'booking': all_bookings[1] if len(all_bookings) > 1 else None,
                },
            ]
            for n in sample_notifs:
                Notification.objects.create(**n)
            self.stdout.write(self.style.SUCCESS("[OK] Sample notifications created"))

        self.stdout.write(self.style.SUCCESS("[DONE] Database seeding completed successfully!"))
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("================================================="))
        self.stdout.write(self.style.WARNING("  Admin Panel: http://127.0.0.1:8000/admin-panel/"))
        self.stdout.write(self.style.WARNING("  Login: admin / admin123"))
        self.stdout.write(self.style.WARNING("================================================="))

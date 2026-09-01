# Mehendi Booking Project Manual

This guide documents the Django project in this repository. It covers local setup, both administration interfaces, and the common content changes needed for the Mehendi/Henna artist website.

## 1. Project Overview

The project has two Django apps:

- `booking`: public website, customer registration/login, services, gallery, reviews, and booking workflow.
- `panel`: custom staff-only studio management panel.

The root configuration is in `mehendi_booking/`. The project currently uses SQLite in `db.sqlite3`, stores uploaded media under `media/`, and serves local static/media files while `DEBUG = True`.

### Important URLs

| Purpose | URL |
|---|---|
| Public website | `http://127.0.0.1:8000/` |
| Django admin | `http://127.0.0.1:8000/admin/` |
| Custom studio panel | `http://127.0.0.1:8000/admin-panel/` |
| Customer login | `http://127.0.0.1:8000/login/` |
| Customer registration | `http://127.0.0.1:8000/register/` |
| Booking page | `http://127.0.0.1:8000/book/` |

The public routes are defined in `booking/urls.py`; the custom panel routes are defined in `panel/urls.py`; both are included by `mehendi_booking/urls.py`.

## 2. How to Start the Project

### Prerequisites

Install Python 3.10 or newer. The project was generated with Django 6.0.2. Because this repository does not currently contain a `requirements.txt`, install the project dependencies manually in a virtual environment.

### Windows PowerShell setup

Open PowerShell in the folder containing `manage.py`:

```powershell
cd "C:\path\to\mehendi_booking"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "Django==6.0.2" Pillow
```

If PowerShell blocks activation, allow scripts for the current user, then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

You can also run the commands through `python` without activating the environment by using `.venv\Scripts\python.exe` explicitly.

### Run migrations

Apply Django's built-in migrations and this project's migrations:

```powershell
python manage.py migrate
```

This creates or updates `db.sqlite3`. Run this command after pulling changes that add or modify migrations.

### Create an administrator

For a secure administrator account, use the interactive command:

```powershell
python manage.py createsuperuser
```

Enter a username, email address, and strong password when prompted. This account is both a Django admin user and a staff user eligible to access the custom panel.

### Optional: load demo data

The repository includes a seed command that creates sample services, gallery items, reviews, notifications, a demo customer, business settings, and an `admin` account if one does not already exist:

```powershell
python manage.py seed_data
```

The seed command uses these demo credentials:

- Admin: `admin` / `admin123`
- Demo customer: `ananya` / `pass123`

Change or remove these credentials before using the project beyond local development. The command deletes and recreates seeded services and gallery items, so do not run it against data you need to preserve.

### Check the installation

Run Django's system checks:

```powershell
python manage.py check
```

### Launch the development server

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Stop the server with `Ctrl+C`.

The development configuration uses `ALLOWED_HOSTS = ['*']`, `DEBUG = True`, a hard-coded development secret key, and local SQLite. These settings are not suitable for production. Before deployment, move secrets to environment variables, set `DEBUG = False`, configure `ALLOWED_HOSTS`, use a production database/server, and configure static/media hosting.

## 3. Administration and Bookings

### Default Django admin

1. Start the server.
2. Visit `http://127.0.0.1:8000/admin/`.
3. Sign in with the superuser created by `createsuperuser`.
4. Use the registered models to manage services, gallery items, bookings, and reviews.

The registrations and admin features are in `booking/admin.py`:

- **Services**: edit prices and featured state from the list; filter by category/featured state.
- **Gallery items**: filter/search items and mark them featured.
- **Bookings**: filter by status, venue, date, or service; search customer details; update status; use bulk status actions.
- **Reviews**: approve/unapprove reviews and filter by rating/date.

`BusinessSettings`, `Payment`, `Notification`, and `TimeSlotBlock` are not registered in the default Django admin. Use the custom panel for those workflows.

### Custom studio panel

Visit `http://127.0.0.1:8000/admin-panel/`. Every custom panel view uses Django's `staff_member_required` decorator. You must be logged in and have `is_staff = True`; normal customer accounts cannot access it.

The panel provides:

- **Dashboard**: booking counts, revenue, recent bookings, and notifications.
- **Notifications**: review alerts and booking/cancellation alerts.
- **Bookings**: search/filter bookings, open details, update booking status, and record payments.
- **Customers**: list non-staff customers, search them, view their bookings/reviews, and enable or disable accounts.
- **Services**: create, edit, activate/deactivate, feature, upload an image, or delete a service.
- **Gallery**: upload/edit/delete designs, add image URLs, categorize items, and feature them.
- **Availability**: block or unblock individual time slots for a date.
- **Reviews**: approve or delete reviews.
- **Reports**: view reporting data.
- **Settings**: edit business identity, contact details, social handle, address, and hours.
- **My Profile**: manage the signed-in staff profile.

The panel is a custom set of views and templates, not a replacement for `/admin/`. Its route prefix is configured as `path('admin-panel/', include('panel.urls'))` in `mehendi_booking/urls.py`.

### Booking behavior

Customers select a service, date, time slot, and venue on `/book/`. A home visit adds `₹500` to the service price. The available-slot API is `/api/available-slots/?date=YYYY-MM-DD`; it excludes non-cancelled bookings and manually blocked slots. Active bookings cannot share the same date/time slot.

A booking can have these statuses: Pending, Confirmed, Completed, Cancelled, or Rejected. The panel's booking detail screen also creates/updates the related payment record.

## 4. How to Make Common Changes

### Phone, email, WhatsApp, social handle, address, and hours

Use the custom panel rather than editing Python defaults:

1. Sign in as a staff user.
2. Open `http://127.0.0.1:8000/admin-panel/settings/`.
3. Update the fields under **Contact Details**, **Operating Hours**, or **Studio Identity**.
4. Click **Save All Settings**.

These values belong to the singleton `BusinessSettings` model in `booking/models.py`. `BusinessSettings.get_settings()` always retrieves or creates the row with primary key `1`. The save handler is in `panel/views.py` and the form is in `panel/templates/panel/settings/form.html`.

**Current implementation note:** the public templates do not currently read these saved fields. The settings page stores them successfully, but public-facing phone/email/hours text and links that are hard-coded in templates will not automatically change. To make the public site use the stored values, update the relevant view context/templates to pass and render `BusinessSettings.get_settings()`.

The model defaults are also in `booking/models.py`:

- `phone`
- `email`
- `whatsapp`
- `instagram`
- `address`
- `mon_fri_hours`
- `sat_hours`
- `sun_hours`

Changing a model default affects newly created settings rows, not an existing row already stored in `db.sqlite3`.

### Business name and tagline

For the database-backed values, use the panel Settings page. For the currently displayed branding, inspect and edit:

- `booking/templates/booking/base.html`: browser title defaults, navigation brand, footer brand, and social links.
- `panel/templates/panel/base_admin.html`: admin-panel title and sidebar brand.
- `booking/templates/booking/home.html` and the other page templates: page-specific headings and promotional copy.

Search the templates for the old business name or text before editing so every occurrence is updated consistently.

### Front-end text

Page-specific text is in these templates:

| Page | Template |
|---|---|
| Home | `booking/templates/booking/home.html` |
| About | `booking/templates/booking/about.html` |
| Services | `booking/templates/booking/services.html` |
| Gallery | `booking/templates/booking/gallery.html` |
| Booking | `booking/templates/booking/booking.html` |
| Login/register | `booking/templates/booking/login.html`, `register.html` |
| Shared header/footer | `booking/templates/booking/base.html` |
| Custom panel | `panel/templates/panel/` and its subdirectories |

Dynamic services, gallery items, reviews, and booking data should normally be changed through the panel. Static marketing copy, artist biography, labels, buttons, titles, and fallback text are edited in the templates. After changing a template, refresh the page; restart the server only if a development issue requires it.

### CSS styles

Public website styles are in `booking/static/booking/css/style.css`. Public JavaScript is in `booking/static/booking/js/script.js`.

Custom panel styles are in `panel/static/panel/css/admin.css`.

Edit existing CSS variables near the beginning of each stylesheet when changing the color palette, typography, shadows, spacing, or border radii. Keep selectors scoped to the relevant app to avoid accidentally changing both the public website and the panel. The public base template loads `booking/css/style.css`; the panel base template loads `panel/css/admin.css`.

### Gallery images

There are two supported storage fields on `GalleryItem`:

- `image`: an uploaded file stored under `MEDIA_ROOT/gallery/`.
- `image_url`: an external URL or static path stored as text.

Recommended workflow:

1. Open `http://127.0.0.1:8000/admin-panel/gallery/`.
2. Choose **Upload Design** or edit an existing item.
3. Enter a title and category.
4. Upload an image file, or paste an image URL.
5. Add description/tags and choose whether it is featured.
6. Save the item.

`MEDIA_ROOT` is `media/` and `MEDIA_URL` is `/media/` in `mehendi_booking/settings.py`. Local uploaded files are served by the development URL configuration while `DEBUG = True`. Back up the `media/` directory separately from the database because SQLite stores the file path, not the image bytes.

**Current implementation note:** the public templates `booking/templates/booking/home.html` and `booking/templates/booking/gallery.html` currently render `item.image_url` directly. The panel preview and model helper know about uploaded `image` files, but uploaded gallery files may not appear on the public pages until those templates use the model's uploaded image URL when present. For the current code, paste a working external URL into `image_url` for reliable public display, or update the templates to use a fallback such as `item.image.url` when `item.image` exists.

Services have the same `image`/`image_url` pattern. Their public cards in `home.html` and `services.html` currently use `service.image_url`, so use a URL there unless the templates are updated for uploaded files.

## 5. Useful Maintenance Commands

Run these from the directory containing `manage.py` with the virtual environment active:

```powershell
python manage.py check
python manage.py showmigrations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py changepassword <username>
python manage.py shell
```

Do not delete `db.sqlite3` unless you intentionally want to remove all local users, bookings, services, gallery records, reviews, payments, and settings. Before structural model changes, back up both `db.sqlite3` and `media/`.

## 6. Quick Troubleshooting

- **`No module named django`**: activate `.venv` or install Django into the interpreter being used.
- **Images do not load**: confirm the URL is reachable, confirm `MEDIA_ROOT`/`MEDIA_URL`, and remember that current public gallery/service templates use `image_url`.
- **Panel redirects to login**: sign in first and verify the user has `is_staff = True`.
- **No services or gallery content**: run `python manage.py seed_data` only on a disposable/demo database, or add records through the panel.
- **Migrations are pending**: run `python manage.py migrate`.
- **A booking slot is unavailable**: check both existing non-cancelled bookings and the panel's Availability screen.

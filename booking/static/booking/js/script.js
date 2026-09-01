/**
 * Mehendi Artistry & Luxury Booking System
 * Dynamic Interactive Scripts (Slots, Lightbox, Price Calculator, Filters)
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initToastAlerts();
  initGalleryLightbox();
  initBookingWizard();
  initStarRatings();
});

/* --------------------------------------------------------------------------
   1. NAVBAR & MOBILE DRAWER
   -------------------------------------------------------------------------- */
function initNavbar() {
  const navbar = document.querySelector('.header-navbar');
  const mobileToggle = document.getElementById('mobile-toggle-btn');
  const mobileDrawer = document.getElementById('mobile-menu-drawer');

  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar?.classList.add('scrolled');
    } else {
      navbar?.classList.remove('scrolled');
    }
  });

  if (mobileToggle && mobileDrawer) {
    mobileToggle.addEventListener('click', () => {
      mobileDrawer.classList.toggle('open');
      const icon = mobileToggle.querySelector('i') || mobileToggle;
      if (mobileDrawer.classList.contains('open')) {
        mobileToggle.innerHTML = '&times;';
      } else {
        mobileToggle.innerHTML = '&#9776;';
      }
    });
  }
}

/* --------------------------------------------------------------------------
   2. TOAST ALERTS
   -------------------------------------------------------------------------- */
function initToastAlerts() {
  const alerts = document.querySelectorAll('.toast-alert');
  alerts.forEach(alert => {
    // Auto dismiss after 6 seconds
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateX(50px)';
      alert.style.transition = 'all 0.4s ease';
      setTimeout(() => alert.remove(), 400);
    }, 6000);

    const closeBtn = alert.querySelector('.toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => alert.remove());
    }
  });
}

/* --------------------------------------------------------------------------
   3. GALLERY LIGHTBOX & FILTERING
   -------------------------------------------------------------------------- */
function initGalleryLightbox() {
  const modal = document.getElementById('gallery-lightbox-modal');
  if (!modal) return;

  const modalImg = document.getElementById('lightbox-target-img');
  const modalTitle = document.getElementById('lightbox-target-title');
  const modalCat = document.getElementById('lightbox-target-cat');
  const modalDesc = document.getElementById('lightbox-target-desc');
  const modalBookBtn = document.getElementById('lightbox-book-btn');
  const closeBtn = document.getElementById('lightbox-close-btn');

  // Open modal on gallery card click
  document.querySelectorAll('.gallery-card').forEach(card => {
    card.addEventListener('click', () => {
      const img = card.getAttribute('data-img');
      const title = card.getAttribute('data-title');
      const cat = card.getAttribute('data-category');
      const desc = card.getAttribute('data-desc') || '';

      if (modalImg) modalImg.src = img;
      if (modalTitle) modalTitle.textContent = title;
      if (modalCat) modalCat.textContent = cat;
      if (modalDesc) modalDesc.textContent = desc;
      if (modalBookBtn) modalBookBtn.href = `/book/`;

      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  });

  function closeModal() {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) closeModal();
  });
}

/* --------------------------------------------------------------------------
   4. BOOKING WIZARD, DYNAMIC SLOTS & PRICE CALCULATOR
   -------------------------------------------------------------------------- */
function initBookingWizard() {
  const serviceSelect = document.getElementById('service-select');
  const dateInput = document.getElementById('booking-date-input');
  const slotSelect = document.getElementById('time-slot-select');
  const slotButtonsContainer = document.getElementById('slot-buttons-container');
  const venueSelect = document.getElementById('venue-type-select');
  const addressGroup = document.getElementById('address-group');

  // Summary elements
  const summaryService = document.getElementById('summary-service-name');
  const summaryDate = document.getElementById('summary-date');
  const summaryTime = document.getElementById('summary-time');
  const summaryVenue = document.getElementById('summary-venue');
  const summaryDuration = document.getElementById('summary-duration');
  const summaryBasePrice = document.getElementById('summary-base-price');
  const summaryTravelPrice = document.getElementById('summary-travel-price');
  const summaryTotalPrice = document.getElementById('summary-total-price');

  if (!serviceSelect || !dateInput) return;

  // Toggle address field based on venue selection
  function updateVenueState() {
    if (!venueSelect) return;
    const isHome = venueSelect.value === 'home';
    if (addressGroup) {
      addressGroup.style.display = isHome ? 'block' : 'none';
      const addressInput = addressGroup.querySelector('textarea, input');
      if (addressInput) addressInput.required = isHome;
    }
    updatePricingSummary();
  }

  if (venueSelect) {
    venueSelect.addEventListener('change', updateVenueState);
    updateVenueState();
  }

  // Update Pricing & Details Summary
  function updatePricingSummary() {
    const selectedOption = serviceSelect.options[serviceSelect.selectedIndex];
    if (!selectedOption || !selectedOption.value) {
      if (summaryService) summaryService.textContent = 'Please select a service';
      if (summaryBasePrice) summaryBasePrice.textContent = '₹0';
      if (summaryTotalPrice) summaryTotalPrice.textContent = '₹0';
      return;
    }

    const price = parseFloat(selectedOption.getAttribute('data-price') || 0);
    const duration = selectedOption.getAttribute('data-duration') || '2.0';
    const isHome = venueSelect && venueSelect.value === 'home';
    const travelFee = isHome ? 500 : 0;
    const total = price + travelFee;

    if (summaryService) summaryService.textContent = selectedOption.text.split('(₹')[0].trim();
    if (summaryDuration) summaryDuration.textContent = `${duration} Hours`;
    if (summaryBasePrice) summaryBasePrice.textContent = `₹${price.toLocaleString('en-IN')}`;
    if (summaryTravelPrice) {
      summaryTravelPrice.textContent = isHome ? '₹500' : '₹0 (In-Studio)';
    }
    if (summaryTotalPrice) summaryTotalPrice.textContent = `₹${total.toLocaleString('en-IN')}`;

    if (summaryDate) {
      const dVal = dateInput.value;
      if (dVal) {
        const dObj = new Date(dVal);
        summaryDate.textContent = dObj.toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
      } else {
        summaryDate.textContent = 'Select a date';
      }
    }

    if (summaryTime) {
      summaryTime.textContent = slotSelect && slotSelect.value ? slotSelect.value : 'Select a time slot';
    }

    if (summaryVenue && venueSelect) {
      summaryVenue.textContent = isHome ? 'Client Location (+ ₹500)' : 'Artist Luxury Studio';
    }
  }

  // Fetch Available Slots dynamically from server for selected Date
  async function fetchAvailableSlots(dateVal) {
    if (!dateVal || !slotButtonsContainer) return;

    slotButtonsContainer.innerHTML = '<div style="padding:15px;text-align:center;color:#6e5b56;font-size:0.9rem;">Checking artist schedule...</div>';

    try {
      const response = await fetch(`/api/available-slots/?date=${encodeURIComponent(dateVal)}`);
      if (!response.ok) throw new Error('Network error');
      const data = await response.json();

      slotButtonsContainer.innerHTML = '';
      const slots = data.slots || [];

      if (slots.length === 0) {
        slotButtonsContainer.innerHTML = '<div style="color:#d32f2f;font-size:0.9rem;">No slots configured for this date.</div>';
        return;
      }

      slots.forEach(slot => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = `slot-btn ${slot.is_available ? '' : 'disabled'}`;
        if (slotSelect && slotSelect.value === slot.value && slot.is_available) {
          btn.classList.add('selected');
        }

        btn.innerHTML = `
          <span class="slot-time">${slot.value}</span>
          <span class="slot-status ${slot.is_available ? 'available' : 'booked'}">
            ${slot.is_available ? '● Available' : '✕ Booked'}
          </span>
        `;

        if (slot.is_available) {
          btn.addEventListener('click', () => {
            // Deselect all
            slotButtonsContainer.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            if (slotSelect) {
              slotSelect.value = slot.value;
            }
            updatePricingSummary();
          });
        } else {
          btn.disabled = true;
          btn.title = 'This slot has already been booked by another client';
        }

        slotButtonsContainer.appendChild(btn);
      });

      // If current select value is not available, reset it
      if (slotSelect && slotSelect.value) {
        const matching = slots.find(s => s.value === slotSelect.value);
        if (!matching || !matching.is_available) {
          slotSelect.value = '';
          updatePricingSummary();
        }
      }

    } catch (err) {
      console.error('Error fetching slots:', err);
      slotButtonsContainer.innerHTML = '<div style="color:#d32f2f;font-size:0.9rem;">Unable to load live availability. You can still choose from the dropdown.</div>';
    }
  }

  // Event Listeners
  serviceSelect.addEventListener('change', updatePricingSummary);
  
  dateInput.addEventListener('change', () => {
    updatePricingSummary();
    fetchAvailableSlots(dateInput.value);
  });

  if (slotSelect) {
    slotSelect.addEventListener('change', () => {
      // Highlight matching button if rendered
      if (slotButtonsContainer) {
        slotButtonsContainer.querySelectorAll('.slot-btn').forEach(b => {
          if (b.querySelector('.slot-time')?.textContent === slotSelect.value) {
            b.classList.add('selected');
          } else {
            b.classList.remove('selected');
          }
        });
      }
      updatePricingSummary();
    });
  }

  // Initial load
  updatePricingSummary();
  if (dateInput.value) {
    fetchAvailableSlots(dateInput.value);
  }
}

/* --------------------------------------------------------------------------
   5. INTERACTIVE STAR RATINGS
   -------------------------------------------------------------------------- */
function initStarRatings() {
  const container = document.getElementById('star-rating-container');
  const hiddenInput = document.getElementById('rating-value-input');
  if (!container || !hiddenInput) return;

  const stars = container.querySelectorAll('.star');

  function highlightStars(rating) {
    stars.forEach(star => {
      const val = parseInt(star.getAttribute('data-rating'), 10);
      if (val <= rating) {
        star.classList.add('active');
      } else {
        star.classList.remove('active');
      }
    });
  }

  stars.forEach(star => {
    star.addEventListener('mouseenter', () => {
      const rating = parseInt(star.getAttribute('data-rating'), 10);
      highlightStars(rating);
    });

    star.addEventListener('click', () => {
      const rating = parseInt(star.getAttribute('data-rating'), 10);
      hiddenInput.value = rating;
      highlightStars(rating);
    });
  });

  container.addEventListener('mouseleave', () => {
    const currentVal = parseInt(hiddenInput.value || 5, 10);
    highlightStars(currentVal);
  });

  // Set default initial 5 stars
  highlightStars(parseInt(hiddenInput.value || 5, 10));
}

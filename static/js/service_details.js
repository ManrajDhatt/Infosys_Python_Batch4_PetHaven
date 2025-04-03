// Function for sidebar
function toggleSidebar() {
	const sidebar = document.getElementById('sidebar');
	const navbar = document.getElementById('navbar');
	const mainContent = document.getElementById('mainContent');

	if (sidebar.classList.contains('show')) {
		sidebar.classList.remove('show');
		navbar.style.left = '0';
		navbar.style.width = '100%';
		mainContent.style.marginLeft = '0';
	} else {
		sidebar.classList.add('show');
		navbar.style.left = '250px';
		navbar.style.width = 'calc(100% - 250px)';
		mainContent.style.marginLeft = '250px';
	}
}

// Function to handle booking from service provider page
function bookService(serviceId) {
	console.log("Navigating to service details page for ID:", serviceId);
	window.location.href = `/service-details/${serviceId}`;
}

// Function to show success modal on service provider page
function showSuccessModalOnProviderPage() {
	const successModal = document.getElementById('success-modal');
	if (successModal) {
		successModal.classList.add('active');
		
		// Reset and restart SVG animation
		const checkmark = successModal.querySelector('.checkmark');
		if (checkmark) {
			// Force a repaint to make animation restart
			checkmark.style.animation = 'none';
			checkmark.offsetHeight; // Trigger repaint
			checkmark.style.animation = 'fill .4s ease-in-out .4s forwards, scale .3s ease-in-out .9s both';
			
			// Reset circle animation
			const circle = checkmark.querySelector('.checkmark-circle');
			if (circle) {
				circle.style.animation = 'none';
				circle.offsetHeight;
				circle.style.animation = 'stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards';
			}
			
			// Reset check animation
			const check = checkmark.querySelector('.checkmark-check');
			if (check) {
				check.style.animation = 'none';
				check.offsetHeight;
				check.style.animation = 'stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards';
			}
		}
	}
}

const providerDataElement = document.getElementById('provider-data');
// Only try to parse provider data if the element exists (for service details page)
if (providerDataElement) {
    const provider = JSON.parse(providerDataElement.textContent);
    
    // Review Data (still hardcoded for now)
    const reviews = [
        {
            text: "An absolutely luxurious experience for my pup! The attention to detail is unmatched.",
            reviewer: "Sarah L.",
            rating: 5
        },
        {
            text: "John's expertise shines through. My dog has never looked better!",
            reviewer: "Mike T.",
            rating: 4.5
        },
        {
            text: "Premium service worth every penny. Exceptional quality and care.",
            reviewer: "Emma R.",
            rating: 4
        }
    ];

    // Render Service Details
    function renderServiceDetails() {
        const serviceDetails = document.getElementById('serviceDetails');
        if (!serviceDetails) return;
        
        serviceDetails.innerHTML = `
            <p><strong>Provider</strong><br>${provider.name}</p>
            <p><strong>Location</strong><br>${provider.address}</p>
            <p><strong>Rate</strong><br>Rs.${provider.hourly_rate}/hour</p>
            <p><strong>Experience</strong><br>${provider.experience}</p>
            <p><strong>Description</strong><br>${provider.description}</p>
            <p><strong>Status</strong><br><span class="status-accepted">${provider.status}</span></p>
        `;
    }

    // Render Reviews
    function renderReviews() {
        const reviewList = document.getElementById('reviewList');
        if (!reviewList) return;
        
        reviewList.innerHTML = reviews.map(review => `
            <div class="review">
                <p>"${review.text}"</p>
                <p class="reviewer">- ${review.reviewer}</p>
            </div>
        `).join('');
    }

    // Format date to a more readable format
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    }
    
    // Format time to 12-hour format
    function formatTime(timeString) {
        const [hours, minutes] = timeString.split(':');
        const hour = parseInt(hours);
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const hour12 = hour % 12 || 12;
        return `${hour12}:${minutes} ${ampm}`;
    }

    // Modal elements
    const bookingModal = document.getElementById('bookingModal');
    const successModal = document.getElementById('successModal');
    const closeModalBtn = document.getElementById('closeModal');
    const cancelBookingBtn = document.getElementById('cancelBooking');
    const confirmBookingBtn = document.getElementById('confirmBooking');
    const closeSuccessBtn = document.getElementById('closeSuccess');
    const closeSuccessModalBtn = document.getElementById('closeSuccessModal');

    // Open booking confirmation modal and populate it with booking details
    function openBookingModal(date, time, duration) {
        const totalCost = provider.hourly_rate * parseInt(duration);
        
        // Populate summary
        document.getElementById('summaryService').textContent = provider.service_name;
        document.getElementById('summaryProvider').textContent = provider.name;
        document.getElementById('summaryDate').textContent = formatDate(date);
        document.getElementById('summaryTime').textContent = formatTime(time);
        document.getElementById('summaryDuration').textContent = `${duration} hour${duration > 1 ? 's' : ''}`;
        document.getElementById('summaryTotal').textContent = `Rs.${totalCost.toLocaleString()}`;
        
        // Show modal
        bookingModal.classList.add('active');
    }

    // Close booking modal
    function closeBookingModal() {
        bookingModal.classList.remove('active');
    }

    // Show success modal
    function showSuccessModal() {
        successModal.classList.add('active');
        
        // Reset and restart SVG animation if needed
        const checkmark = document.querySelector('.checkmark');
        if (checkmark) {
            // Force a repaint to make animation restart
            checkmark.style.animation = 'none';
            checkmark.offsetHeight; // Trigger repaint
            checkmark.style.animation = 'fill .4s ease-in-out .4s forwards, scale .3s ease-in-out .9s both';
            
            // Reset circle animation
            const circle = document.querySelector('.checkmark-circle');
            if (circle) {
                circle.style.animation = 'none';
                circle.offsetHeight;
                circle.style.animation = 'stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards';
            }
            
            // Reset check animation
            const check = document.querySelector('.checkmark-check');
            if (check) {
                check.style.animation = 'none';
                check.offsetHeight;
                check.style.animation = 'stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards';
            }
        }
    }

    // Close success modal
    function closeSuccessModal() {
        successModal.classList.remove('active');
    }

    // Event listeners for modal
    if (closeModalBtn) closeModalBtn.addEventListener('click', closeBookingModal);
    if (cancelBookingBtn) cancelBookingBtn.addEventListener('click', closeBookingModal);
    if (closeSuccessBtn) closeSuccessBtn.addEventListener('click', closeSuccessModal);
    if (closeSuccessModalBtn) closeSuccessModalBtn.addEventListener('click', closeSuccessModal);

    // Handle Form Submission
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        bookingForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const date = document.getElementById('date').value;
            const time = document.getElementById('time').value;
            const duration = document.getElementById('duration').value;
            
            // Validate form fields
            if (!date || !time || !duration) {
                alert('Please fill out all booking details');
                return;
            }
            
            // Open booking confirmation modal
            openBookingModal(date, time, duration);
        });
    }
    
    // Handle booking confirmation
    if (confirmBookingBtn) {
        confirmBookingBtn.addEventListener('click', () => {
            // Get values from the form
            const date = document.getElementById('date').value;
            const time = document.getElementById('time').value;
            const duration = document.getElementById('duration').value;
            const totalCost = provider.hourly_rate * parseInt(duration);
            
            // Show loading state on the confirm button
            confirmBookingBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            confirmBookingBtn.disabled = true;
            
            // Prepare data for API
            const data = { 
                date, 
                time, 
                duration, 
                totalCost, 
                service_id: provider.service_id 
            };
            
            console.log("Sending booking request with data:", data);
            
            // Make API call to book service
            fetch("/book-service", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(data),
                credentials: 'include' // Include credentials for session cookies
            })
            .then(response => {
                console.log("Response status:", response.status);
                // Handle login redirect for 401 status
                if (response.status === 401) {
                    alert("Please log in to book services");
                    window.location.href = "/login";
                    throw new Error("Not logged in");
                }
                
                if (!response.ok) {
                    return response.json().then(errorData => {
                        throw new Error(errorData.error || "Something went wrong");
                    });
                }
                
                return response.json();
            })
            .then(data => {
                // Close booking modal
                closeBookingModal();
                
                console.log("Booking response:", data);
                
                if (data.error) {
                    // Show error message
                    alert("Booking Failed: " + data.error);
                } else {
                    // Only add to cart if booking succeeded and we have a booking_id
                    if (data.booking_id) {
                        console.log("Booking ID received:", data.booking_id);
                        // Convert booking_id to string if it's not already
                        const bookingIdString = String(data.booking_id);
                        addBookingToCart(bookingIdString);
                    } else {
                        console.error("No booking_id received in response");
                        // Show success modal anyway since booking was created
                        showSuccessModal();
                        
                        // Reset form
                        document.getElementById('bookingForm').reset();
                        document.getElementById('costPreview').innerHTML = '';
                    }
                }
                
                // Reset button state
                confirmBookingBtn.innerHTML = 'Confirm Booking';
                confirmBookingBtn.disabled = false;
            })
            .catch(error => {
                console.error("Fetch Error:", error);
                
                // Close booking modal
                closeBookingModal();
                
                // Don't show error if it was a login redirect
                if (error.message !== "Not logged in") {
                    // Show error message
                    alert("Failed to book your appointment. Please try again!");
                }
                
                // Reset button state
                confirmBookingBtn.innerHTML = 'Confirm Booking';
                confirmBookingBtn.disabled = false;
            });
        });
    }
    
    // Function to Add Booking to Cart
    function addBookingToCart(bookingId) {
        const payload = { booking_id: bookingId };
        console.log("Adding to cart with payload:", payload);
        
        fetch("/cart/add", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload),
            credentials: 'include' // Include credentials for session cookies
        })
        .then(response => {
            console.log("Cart response status:", response.status);
            // Handle login redirect for 401 status
            if (response.status === 401) {
                alert("Please log in to add to cart");
                window.location.href = "/login";
                throw new Error("Not logged in");
            }
            
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || "Something went wrong");
                });
            }
            
            return response.json();
        })
        .then(data => {
            console.log("Cart response data:", data);
            if (data.error) {
                console.error("Cart Error:", data.error);
                alert("Failed to add booking to cart: " + data.error);
            } else {
                // Show success modal
                showSuccessModal();
                
                // Update cart count if element exists
                const cartCount = document.getElementById("cart-count");
                if (cartCount && data.cart_count) {
                    cartCount.textContent = data.cart_count;
                }
                
                // Reset form
                document.getElementById('bookingForm').reset();
                document.getElementById('costPreview').innerHTML = '';
            }
        })
        .catch(error => {
            console.error("Cart Fetch Error:", error);
            // Don't show error if it was a login redirect
            if (error.message !== "Not logged in") {
                alert("Error adding booking to cart. Please try again!");
            }
        });
    }

    // Real-time Cost Preview
    const durationField = document.getElementById('duration');
    if (durationField) {
        durationField.addEventListener('change', (e) => {
            const duration = e.target.value;
            if (duration) {
                const totalCost = provider.hourly_rate * parseInt(duration);
                document.getElementById('costPreview').innerHTML = `Total: Rs.${totalCost.toLocaleString()}`;
            } else {
                document.getElementById('costPreview').innerHTML = '';
            }
        });
    }

    // Set minimum date to today
    const dateField = document.getElementById('date');
    if (dateField) {
        dateField.setAttribute('min', new Date().toISOString().split('T')[0]);
    }

    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM fully loaded'); 
        renderServiceDetails();
        renderReviews();
        
        // Fetch current cart count
        fetchCartCount();
    });

    // Function to fetch cart count
    function fetchCartCount() {
        fetch('/api/cart_count', {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            const cartCountElement = document.getElementById('cart-count');
            if (cartCountElement && data.cart_count) {
                cartCountElement.textContent = data.cart_count;
            }
        })
        .catch(error => {
            console.error('Error fetching cart count:', error);
        });
    }
}
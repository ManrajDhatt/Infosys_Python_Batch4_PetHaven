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

/****************************************** fetching dogs details from the api for listing and checking the filters for apply changes in the listing */
document.addEventListener("DOMContentLoaded", function () {
  // Check if we're on a page with dog listings before fetching and setting up filters
  if (document.getElementById("dogGrid")) {
    fetchDogs();
    
    // Filter event listeners - only attach if elements exist
    const breedFilter = document.getElementById("breedFilter");
    const ageFilter = document.getElementById("ageFilter");
    const minPrice = document.getElementById("minPrice");
    const maxPrice = document.getElementById("maxPrice");
    const searchInput = document.getElementById("searchInput");
    
    if (breedFilter) breedFilter.addEventListener("change", applyFilters);
    if (ageFilter) ageFilter.addEventListener("change", applyFilters);
    if (minPrice) minPrice.addEventListener("input", applyFilters);
    if (maxPrice) maxPrice.addEventListener("input", applyFilters);
    if (searchInput) searchInput.addEventListener("keyup", applyFilters);
  }
  
  // Always try to update cart count if the element exists
  updateCartCount();
});

let allDogs = [];
const DOGS_PER_PAGE = 12;
let currentPage = 1;

function fetchDogs() {
  fetch("/api/dogs")
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((dogs) => {
      allDogs = dogs;
      const maxDogPrice = dogs.reduce(
        (max, dog) => Math.max(max, dog.price),
        0
      );
      
      const maxPriceElement = document.getElementById("maxPrice");
      const maxPriceValueElement = document.getElementById("maxPriceValue");
      
      if (maxPriceElement) maxPriceElement.value = maxDogPrice;
      if (maxPriceValueElement) maxPriceValueElement.textContent = `Max Price: Rs.${maxDogPrice}`;
      
      applyFilters(); // Initial display with filters
    })
    .catch((error) => console.error("Error fetching dogs:", error));
}

/********************************* function for displaying dogs in a list ***********************************/
function displayDogs(dogs) {
  const dogGrid = document.getElementById("dogGrid");
  dogGrid.innerHTML = "";

  if (dogs.length === 0) {
    dogGrid.innerHTML = "<p>No dogs match your filters.</p>";
    updatePagination(0);
    return;
  }

  // Calculate pagination
  const totalPages = Math.ceil(dogs.length / DOGS_PER_PAGE);
  const startIndex = (currentPage - 1) * DOGS_PER_PAGE;
  const endIndex = startIndex + DOGS_PER_PAGE;
  const paginatedDogs = dogs.slice(startIndex, endIndex);

  paginatedDogs.forEach((dog) => {
    const dogCard = document.createElement("div");
    dogCard.classList.add("dog-card");

    dogCard.innerHTML = `
      <img src="${dog.image}" alt="${dog.name}" style="width: 100%; height: 200px; object-fit: cover;">
      <h3>${dog.name}</h3>
      <p>Breed: ${dog.breed}</p>
      <p>Age: ${dog.age}</p>
      <p>Price: Rs.${dog.price}</p>      
      <div class="dog-card-button-container">
        <button class="add-to-cart" data-id="${dog.id}">Add to Cart</button>
      </div>
    `;
    const dogCardImage = dogCard.querySelector("img");
    dogCardImage.addEventListener("click", function(){
      displayDogDetails(dog);
    })
    dogGrid.appendChild(dogCard);
  });

  updatePagination(totalPages, dogs.length);
  attachCartListeners();
}

function displayDogDetails(dog) {
  const detailsSection = document.getElementById("dogDetails");
  if (!detailsSection) return; // Exit if element doesn't exist
  
  detailsSection.innerHTML = `
      <div class="dog-info">
          <img src="${dog.image}" alt="${dog.name}" />
          <h2>${dog.name}</h2>
          <p><strong>Breed:</strong> ${dog.breed}</p>
          <p><strong>Age:</strong> ${dog.age}</p>
          <p><strong>Price:</strong> Rs.${dog.price}</p>
          <p><strong>Vaccinated:</strong> ${dog.vaccinated}</p>
          <p><strong>Description:</strong> ${dog.description}</p>
      </div>
  `;
  const modal = document.getElementById("dogDetailsModal");
  if (modal) modal.style.display = "block"; // Show modal only if it exists
}

function closeModal() {
  const modal = document.getElementById("dogDetailsModal");
  if (modal) modal.style.display = "none"; // Hide modal only if it exists
}

// Only attach event listeners if elements exist
document.addEventListener("DOMContentLoaded", function() {
  const closeModalBtn = document.getElementById("closeModal");
  const dogDetailsModal = document.getElementById("dogDetailsModal");
  
  if (closeModalBtn) {
    closeModalBtn.addEventListener("click", closeModal);
  }
  
  if (dogDetailsModal) {
    window.addEventListener("click", function(event) {
      if (event.target === dogDetailsModal) {
        closeModal();
      }
    });
  }
});

/**************************************** function for updating pagination ***********************************/
function updatePagination(totalPages, totalItems) {
  const paginationContainer = document.createElement("div");
  paginationContainer.className = "pagination";

  // Previous Button
  const prevButton = document.createElement("button");
  prevButton.textContent = "Previous";
  prevButton.disabled = currentPage === 1;
  prevButton.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      applyFilters();
    }
  });
  paginationContainer.appendChild(prevButton);

  // Page Numbers
  for (let i = 1; i <= totalPages; i++) {
    const pageButton = document.createElement("button");
    pageButton.textContent = i;
    pageButton.classList.toggle("active", i === currentPage);
    pageButton.addEventListener("click", () => {
      currentPage = i;
      applyFilters();
    });
    paginationContainer.appendChild(pageButton);
  }

  // Next Button
  const nextButton = document.createElement("button");
  nextButton.textContent = "Next";
  nextButton.disabled = currentPage === totalPages;
  nextButton.addEventListener("click", () => {
    if (currentPage < totalPages) {
      currentPage++;
      applyFilters();
    }
  });
  paginationContainer.appendChild(nextButton);

  // Page Info
  const pageInfo = document.createElement("span");
  const start = (currentPage - 1) * DOGS_PER_PAGE + 1;
  const end = Math.min(currentPage * DOGS_PER_PAGE, totalItems);
  pageInfo.textContent = ` Showing ${start}-${end} of ${totalItems} dogs`;
  paginationContainer.appendChild(pageInfo);

  const existingPagination = document.querySelector(".pagination");
  if (existingPagination) {
    existingPagination.remove();
  }
  document.querySelector(".dog-listing").appendChild(paginationContainer);
}

/************************************ function for appling filters ******************************************/
function applyFilters() {
  const breedFilter = document.getElementById("breedFilter");
  const ageFilter = document.getElementById("ageFilter");
  const minPrice = document.getElementById("minPrice");
  const maxPrice = document.getElementById("maxPrice");
  const searchInput = document.getElementById("searchInput");
  const minPriceValueElement = document.getElementById("minPriceValue");
  const maxPriceValueElement = document.getElementById("maxPriceValue");
  
  // Exit if we're not on a page with filters
  if (!breedFilter || !ageFilter || !minPrice || !maxPrice || !searchInput) {
    return;
  }
  
  const breedFilterValue = breedFilter.value;
  const ageFilterValue = ageFilter.value;
  const minPriceVal = parseInt(minPrice.value) || 0;
  const maxPriceVal = parseInt(maxPrice.value) || Infinity;
  const searchTermValue = searchInput.value.toLowerCase();

  if (minPriceValueElement) minPriceValueElement.textContent = `Min Price: Rs.${minPriceVal}`;
  if (maxPriceValueElement) maxPriceValueElement.textContent = `Max Price: Rs.${maxPriceVal}`;

  const filteredDogs = allDogs.filter((dog) => {
    const nameMatch = dog.name.toLowerCase().includes(searchTermValue);
    const breedMatch = dog.breed.toLowerCase().includes(searchTermValue);
    const descriptionMatch = dog.description
      ? dog.description.toLowerCase().includes(searchTermValue)
      : false;
    return (
      (breedFilterValue === "" || dog.breed === breedFilterValue) &&
      (ageFilterValue === "" || dog.age === ageFilterValue) &&
      dog.price >= minPriceVal &&
      dog.price <= maxPriceVal &&
      (nameMatch || breedMatch || descriptionMatch)
    );
  });

  displayDogs(filteredDogs);
}

/********************************** function for updating cart count on page load ****************************/
document.addEventListener("DOMContentLoaded", function () {
    fetchDogs();
    updateCartCount();  // Fetch and update cart count on page load
});

/***************************************** function to fetch cart count from backend *************************/
function updateCartCount() {
    fetch("/api/cart_count")
        .then(response => response.json())
        .then(data => {
            const cartCountElement = document.getElementById("cart-count");
            if (cartCountElement) {
                cartCountElement.textContent = data.cart_count;  // Update UI only if element exists
            }
        })
        .catch(error => console.error("Error fetching cart count:", error));
}

/*************************************** function for add to cart feature ************************************/
function attachCartListeners() {
    document.querySelectorAll(".add-to-cart").forEach(button => {
        button.addEventListener("click", function () {
            let dogId = this.getAttribute("data-id");

            fetch("/cart/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ dog_id: dogId })
            })
            .then(response => response.json())
            .then(data => {
                // Show beautiful notification instead of alert
                showNotification('addToCartNotification');
                
                // Update dog name in notification if possible
                const dogCard = this.closest('.dog-card');
                if (dogCard) {
                    const dogName = dogCard.querySelector('h3').textContent;
                    document.querySelector('#addToCartNotification .notification-title').textContent = 
                        `${dogName} added to your cart!`;
                }
                
                updateCartCount();  // Call the function to update cart count
            })
            .catch(error => console.error("Error adding to cart:", error));
        });
    });
}

// Function to show notification
function showNotification(notificationId) {
    const notification = document.getElementById(notificationId);
    if (notification) {
        notification.classList.add('show');
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            closeNotification(notificationId);
        }, 5000);
    }
}

// Function to close notification
function closeNotification(notificationId) {
    const notification = document.getElementById(notificationId);
    if (notification) {
        notification.classList.remove('show');
    }
}

// Check for order success parameter in URL
document.addEventListener("DOMContentLoaded", function() {
    // Removed URL check to avoid showing order success notification on homepage
    // Now it's shown on the order confirmation page directly
});

/************************************** function for remove from cart feature ********************************/
function attachRemoveListeners() {
    document.querySelectorAll(".remove-from-cart").forEach(button => {
        button.addEventListener("click", function () {
            let dogId = this.getAttribute("data-id");

            fetch("/cart/remove", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ dog_id: dogId })
            })
            .then(response => response.json())
            .then(data => {
                // No need to alert here as cart page has its own notification system
                updateCartCount();  // Update cart count
                removeDogFromUI(dogId);  // Remove dog from UI without reloading
            })
            .catch(error => console.error("Error removing from cart:", error));
        });
    });
}

/*********************************** function to remove item from UI without reloading **********************/
function removeDogFromUI(dogId) {
    let cartItem = document.querySelector(`.cart-item[data-id='${dogId}']`);
    if (cartItem) {
        cartItem.remove();
    }

    // If cart is empty after removal, show "empty cart" message
    if (document.querySelectorAll(".cart-item").length === 0) {
        document.getElementById("cart-list").innerHTML = "<p>Your cart is empty.</p>";
    }
}
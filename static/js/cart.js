document.addEventListener("DOMContentLoaded", function () {
    function addToCart(itemId, type) {
        let requestData = {};
        if (type === "dog") {
            requestData.dog_id = itemId;
        } else if (type === "booking") {
            requestData.booking_id = itemId;
        }

        fetch("/cart/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData),
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                document.getElementById("cart-count").textContent = data.cart_count; // Update cart count dynamically
            })
            .catch(error => console.error("Error adding to cart:", error));
    }

    function removeFromCart(itemId, type) {
        let requestData = {};
        if (type === "dog") {
            requestData.dog_id = itemId;
        } else if (type === "booking") {
            requestData.booking_id = itemId;
        }

        fetch("/cart/remove", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData),
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                document.getElementById("cart-count").textContent = data.cart_count; // Update cart count dynamically
                fetchCartData(); // Refresh cart items
            })
            .catch(error => console.error("Error removing from cart:", error));
    }

    document.querySelectorAll(".remove-from-cart").forEach(button => {
        button.addEventListener("click", function () {
            let itemId = this.getAttribute("data-id");
            let itemType = this.getAttribute("data-type");
            removeFromCart(itemId, itemType);
        });
    });

    // Example usage:
    document.querySelector(".add-to-cart-dog").addEventListener("click", function () {
        let dogId = this.getAttribute("data-id");
        addToCart(dogId, "dog");
    });

    document.querySelector(".add-to-cart-booking").addEventListener("click", function () {
        let bookingId = this.getAttribute("data-id");
        addToCart(bookingId, "booking");
    });
});
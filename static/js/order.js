document.addEventListener("DOMContentLoaded", function () {
    document.querySelector(".confirm-order").addEventListener("click", function () {
        const address = document.getElementById("address").value;
        const city = document.getElementById("city").value;
        const state = document.getElementById("state").value;
        const zip = document.getElementById("zip").value;

        fetch("/place-order", {  // Create order on confirmation, not checkout
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                address: address,
                city: city,
                state: state,
                zip: zip
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message); // Show success message
                window.location.href = `/order-confirm?order_id=${data.order_id}`;
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Failed to place order. Please try again!");
        });
    });
});
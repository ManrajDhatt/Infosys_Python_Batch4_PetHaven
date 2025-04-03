document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".approve-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            fetch(this.dataset.url, { method: "POST" })
                .then(response => {
                    if (response.ok) {
                        window.location.href = "/admin_dashboard"; // Redirect to Service Provider Dashboard
                    } else {
                        alert("Approval failed. Try again.");
                    }
                })
                .catch(error => console.error("Error:", error));
        });
    });

    document.querySelectorAll(".reject-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            fetch(this.dataset.url, { method: "POST" })
                .then(response => {
                    if (response.ok) {
                        window.location.href = "/admin_dashboard"; // Redirect to Get Started Page
                    } else {
                        alert("Rejection failed. Try again.");
                    }
                })
                .catch(error => console.error("Error:", error));
        });
    });
});

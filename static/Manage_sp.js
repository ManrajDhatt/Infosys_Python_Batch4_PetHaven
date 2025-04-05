document.addEventListener("DOMContentLoaded", function () {
    console.log("Manage_sp.js loaded");

    // Approve button handler
    document.querySelectorAll(".approve-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const url = this.dataset.url;
            const card = this.closest(".provider-card");

            fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(response => {
                if (response.ok) {
                    alert("Service Provider Approved!");
                    // Remove card from DOM
                    card.remove();
                } else {
                    alert("Failed to approve provider.");
                }
            })
            .catch(error => {
                console.error("Error approving provider:", error);
                alert("An error occurred.");
            });
        });
    });

    // Reject button handler
    document.querySelectorAll(".reject-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const url = this.dataset.url;
            const card = this.closest(".provider-card");

            fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(response => {
                if (response.ok) {
                    alert("Service Provider Rejected!");
                    // Remove card from DOM
                    card.remove();
                } else {
                    alert("Failed to reject provider.");
                }
            })
            .catch(error => {
                console.error("Error rejecting provider:", error);
                alert("An error occurred.");
            });
        });
    });
});

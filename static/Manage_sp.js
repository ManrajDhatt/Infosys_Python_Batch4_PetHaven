document.addEventListener("DOMContentLoaded", function () {
    console.log("Manage_sp.js loaded");
    
    document.querySelectorAll(".approve-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            console.log("Approve button clicked:", this.dataset.url);
            
            fetch(this.dataset.url, { 
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(response => {
                console.log("Response status:", response.status);
                if (response.ok) {
                    alert("Service provider approved successfully!");
                    window.location.href = "/admin_dashboard"; // Redirect or refresh
                } else {
                    alert("Approval failed. Please try again.");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("Error occurred: " + error);
            });
        });
    });

    document.querySelectorAll(".reject-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            console.log("Reject button clicked:", this.dataset.url);
            
            fetch(this.dataset.url, { 
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(response => {
                console.log("Response status:", response.status);
                if (response.ok) {
                    alert("Service provider rejected successfully!");
                    window.location.href = "/admin_dashboard"; // Redirect or refresh
                } else {
                    alert("Rejection failed. Please try again.");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("Error occurred: " + error);
            });
        });
    });
});
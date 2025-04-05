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

document.addEventListener("DOMContentLoaded", function () {
    fetchDogs();
});

// Fetch and display all dogs
function fetchDogs() {
    fetch("/api/dogs")
        .then(response => response.json())
        .then(data => {
            const dogList = document.getElementById("dog-list");
            dogList.innerHTML = ""; 
            data.forEach(dog => {
                const dogItem = document.createElement("div");
                dogItem.classList.add("dog-item");
                dogItem.innerHTML = `
                    <img src="${dog.image}" alt="${dog.name}">
                    <h3>${dog.name}</h3>
                    <p>Breed: ${dog.breed}</p>
                    <p>Age: ${dog.age} years</p>
                    <p>Price: ₹${dog.price}</p>
                    <p>${dog.description}</p>
                    <div class="dog-card-button-container">
                        <button onclick="editDog('${dog.id}')">Edit</button>
                        <button onclick="deleteDog('${dog.id}')">Delete</button>
                    </div>
                `;
                dogList.appendChild(dogItem);
            });
        })
        .catch(error => console.error("Error fetching dogs:", error));
}

// Delete a dog
function deleteDog(dogId) {
    if (confirm("Are you sure you want to delete this dog?")) {
        fetch(`/admin/dogs/delete/${dogId}`, { method: "DELETE" })  // Corrected URL
            .then(response => response.json())
            .then(() => {
                alert("Dog deleted successfully!");
                fetchDogs();
            })
            .catch(error => console.error("Error deleting dog:", error));
    }
}

// Show add dog form
function showAddDogForm() {
    document.getElementById("add-dog-form").classList.toggle("hidden");
}

// Add a new dog
document.getElementById("dog-form").addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData();  // Use FormData
    formData.append("name", document.getElementById("dog-name").value.trim());
    formData.append("breed", document.getElementById("dog-breed").value.trim());
    formData.append("age", document.getElementById("dog-age").value.trim());
    formData.append("price", document.getElementById("dog-price").value.trim());
    formData.append("description", document.getElementById("dog-description").value.trim());
    formData.append("image", document.getElementById("dog-image").files[0]);  // Image file

    fetch("/admin/dogs/add", {
        method: "POST",
        body: formData  // No need for JSON.stringify
    })
    .then(response => response.json())
    .then(() => {
        document.getElementById("dog-form").reset();
        alert("Dog added successfully!");
        fetchDogs();
    })
    .catch(error => console.error("Error adding dog:", error));
});

// Edit a dog
function editDog(dogId) {
    const newName = prompt("Enter new name:");
    const newPrice = prompt("Enter new price:");

    if (newName && newPrice) {
        fetch(`/admin/dogs/edit/${dogId}`, {   // Corrected URL
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: newName, price: newPrice })
        })
        .then(response => response.json())
        .then(() => {
            alert("Dog updated successfully!");
            fetchDogs();
        })
        .catch(error => console.error("Error updating dog:", error));
    }
}

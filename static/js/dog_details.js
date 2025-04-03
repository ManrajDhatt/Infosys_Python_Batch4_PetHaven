document.addEventListener("DOMContentLoaded", function () {
  const dogId = window.location.pathname.split("/").pop(); // Extract dog ID from URL

  fetch(`/api/dogs/${dogId}`)
    .then((response) => response.json())
    .then((dog) => {
      const dogDetails = document.getElementById("dogDetails");
      dogDetails.innerHTML = `
                <img src="${dog.image}" alt="${dog.name}">
                <h2>${dog.name}</h2>
                <p><strong>Breed:</strong> ${dog.breed}</p>
                <p><strong>Age:</strong> ${dog.age}</p>
                <p><strong>Price:</strong> Rs.${dog.price}</p>
                <button onclick="addToCart(${dog.id})">Add to Cart</button>
            `;
    })
    .catch((error) => console.error("Error fetching dog details:", error));
});

// Mock function for adding to cart (Can be extended later)
function addToCart(dogId) {
  alert(`Dog ID ${dogId} added to cart!`);
}

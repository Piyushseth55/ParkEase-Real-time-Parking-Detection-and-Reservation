document.addEventListener("DOMContentLoaded", () => {
    const spotsContainer = document.getElementById('parking-spots');

    // Fetch parking data from the backend
    fetch('http://localhost:5000/parking')
        .then(response => response.json())
        .then(parkingData => {
            parkingData.forEach(spot => {
                // Create parking spot element
                const spotDiv = document.createElement('div');
                spotDiv.className = `parking-spot ${spot.status}`;
                spotDiv.innerHTML = `<div class="parking-spot-id">${spot.id}</div>`;
                spotsContainer.appendChild(spotDiv);
            });
        })
        .catch(error => console.error('Error fetching parking data:', error));
});

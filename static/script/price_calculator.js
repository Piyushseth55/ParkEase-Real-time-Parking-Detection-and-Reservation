const parkingSlider = document.getElementById('parking-hours');
const selectedHoursText = document.getElementById('selected-hours');
const calculateBtn = document.getElementById('calculate-btn');
const priceDisplay = document.getElementById('calculated-price');
const parkingTypeText = document.getElementById('parking-type');
const openRoofBtn = document.getElementById('open-roof-btn');
const innerBtn = document.getElementById('inner-btn');

let selectedParkingType = 'Open Roof Parking';
let selectedRate = 2; // Default rate for open roof parking

// Set Open Roof Parking as the default selection
window.addEventListener('DOMContentLoaded', () => {
    openRoofBtn.classList.add('selected-btn');
    innerBtn.classList.remove('selected-btn');
    parkingTypeText.textContent = `Parking Type: ${selectedParkingType}`;
    parkingTypeText.style.display = 'block';
    updatePrice();  // Update price on page load with default settings
});

// Update the displayed value when the slider is changed
parkingSlider.addEventListener('input', () => {
    const hours = parkingSlider.value;
    selectedHoursText.textContent = `Selected: ${hours} Hour${hours > 1 ? 's' : ''}`;
    updatePrice();  // Update price automatically when the slider is adjusted
});

// Update the parking type when the buttons are clicked
openRoofBtn.addEventListener('click', () => {
    selectedParkingType = 'Open Roof Parking';
    selectedRate = 2; // Open roof parking rate
    parkingTypeText.textContent = `Parking Type: ${selectedParkingType}`;
    parkingTypeText.style.display = 'block';
    
    // Change selected button style
    openRoofBtn.classList.add('selected-btn');
    innerBtn.classList.remove('selected-btn');
    updatePrice();  // Update price when the parking type is changed
});

innerBtn.addEventListener('click', () => {
    selectedParkingType = 'Inner Parking';
    selectedRate = 3; // Inner parking rate
    parkingTypeText.textContent = `Parking Type: ${selectedParkingType}`;
    parkingTypeText.style.display = 'block';
    
    // Change selected button style
    innerBtn.classList.add('selected-btn');
    openRoofBtn.classList.remove('selected-btn');
    updatePrice();  // Update price when the parking type is changed
});

// Function to update the price automatically
function updatePrice() {
    const hours = parseInt(parkingSlider.value);
    const price = calculatePrice(hours, selectedRate);
    priceDisplay.textContent = `Price: $${price.toFixed(2)}`;
}

// Function to calculate the price
function calculatePrice(hours, rate) {
    return hours * rate;
}

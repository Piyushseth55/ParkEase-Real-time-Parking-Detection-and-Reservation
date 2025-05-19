let totalSpaces = 50;
let availableSpaces = 30;

function bookSlot() {
    if (availableSpaces > 0) {
        availableSpaces--;
        document.getElementById("availableSpaces").innerText = availableSpaces;
        alert("Parking slot booked successfully!");
    } else {
        alert("No available parking spaces.");
    }
}

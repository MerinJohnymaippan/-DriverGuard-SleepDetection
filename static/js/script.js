const statusElement = document.getElementById("status");

// Function to fetch detection status from Flask backend
async function fetchDetectionStatus() {
    try {
        const response = await fetch("/detection_status");
        const data = await response.json();

        if (data.phone_detected) {
            statusElement.textContent = "📱 Phone in Use!";
            statusElement.classList.remove("safe", "drowsy");
            statusElement.classList.add("phone");
        } else if (data.drowsy) {
            statusElement.textContent = "😴 Drowsiness Detected!";
            statusElement.classList.remove("safe", "phone");
            statusElement.classList.add("drowsy");
        } else {
            statusElement.textContent = "✅ No Distraction";
            statusElement.classList.remove("phone", "drowsy");
            statusElement.classList.add("safe");
        }
    } catch (error) {
        console.error("Error fetching detection status:", error);
    }
}

// Update detection status every second
setInterval(fetchDetectionStatus, 1000);

// Wait for the DOM to load before executing the script
document.addEventListener("DOMContentLoaded", function() {
    // Fetch data from a script tag's JSON dataset
    const eventStatsElement = document.getElementById("eventStatsData");
    if (!eventStatsElement) {
        console.error("No event stats data found!");
        return;
    }

    // Parse the JSON data embedded in the HTML template
    const eventStats = JSON.parse(eventStatsElement.textContent);

    // Extract event data
    const eventTitles = eventStats.map(event => event.event_title);
    const eventParticipants = eventStats.map(event => event.total_participants);
    const eventRevenue = eventStats.map(event => event.total_fees_collected);

    console.log("Event Titles:", eventTitles);
    console.log("Participants:", eventParticipants);
    console.log("Revenue:", eventRevenue);

    // Here you can now use these variables to create charts using Chart.js or another library
});



document.addEventListener("DOMContentLoaded", function () {
    const eventStatsData = JSON.parse(document.getElementById("eventStatsData").textContent);
    
    const labels = eventStatsData.map(event => event.event_title);
    const participants = eventStatsData.map(event => event.total_participants);

    const ctx = document.getElementById("eventChart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Total Participants",
                data: participants,
                backgroundColor: "rgba(85, 21, 248, 0.8)",
                borderWidth: 1,
                borderColor: "rgba(85, 21, 248, 1)",
                maxBarThickness:50
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,  
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Events",
                        font: {
                            size: 14,
                            weight: "bold"
                        }
                    },
                    ticks: {
                        maxRotation: 90,  // Prevent tilting
                        minRotation: 60
                    },
                    grid: {
                        display: false  // Hide gridlines on X-axis
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "No. of Participants",
                        font: {
                            size: 14,
                            weight: "bold"
                        }
                    },
                    ticks: {
                        beginAtZero: true,
                        stepSize: 1,  // Ensures whole numbers only
                        precision: 0
                    },
                    grid: {
                        drawBorder: false, 
                        color: "rgba(200, 200, 200, 0.3)"  // Subtle grid lines
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        font: {
                            size: 14
                        },
                        padding: 20  // Space around legend label
                    },
                    position: "top"
                }
            }
        }
    });
});

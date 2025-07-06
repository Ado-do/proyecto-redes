async function updateDashboard() {
  const response = await fetch("/api/readings?limit=50");
  const data = await response.json();

  // Update temperature chart
  updateChart(
    "temp-chart",
    data.map((d) => d.temperature),
  );

  // Update alerts
  const latest = data[0];
  if (latest.temperature > 100) {
    document.getElementById("temp-alert").textContent =
      `ALERT: High temperature (${latest.temperature}°C)`;
  }
}

function updateChart(elementId, values) {
  const ctx = document.getElementById(elementId).getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: { labels: values.map((_, i) => i), datasets: [{ data: values }] },
  });
}

setInterval(updateDashboard, 5000); // Update every 5 seconds

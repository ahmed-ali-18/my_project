document.addEventListener("DOMContentLoaded", () => {
  fetch("/admin/analytics-data")
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("totalComplaints").textContent = data.counts.total;
      document.getElementById("pendingComplaints").textContent = data.counts.pending;
      document.getElementById("resolvedComplaints").textContent = data.counts.resolved;
      document.getElementById("delayedComplaints").textContent = data.counts.delayed;

      const areaLabels = data.by_area.map((x) => x.area);
      const areaCounts = data.by_area.map((x) => x.count);

      new Chart(document.getElementById("areaChart"), {
        type: "bar",
        data: {
          labels: areaLabels,
          datasets: [
            {
              label: "Complaints",
              data: areaCounts,
              backgroundColor: "rgba(54, 162, 235, 0.6)",
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
          },
        },
      });

      const catLabels = data.by_category.map((x) => x.category);
      const catCounts = data.by_category.map((x) => x.count);

      new Chart(document.getElementById("categoryChart"), {
        type: "pie",
        data: {
          labels: catLabels,
          datasets: [
            {
              data: catCounts,
              backgroundColor: [
                "#0d6efd",
                "#198754",
                "#ffc107",
                "#dc3545",
                "#20c997",
                "#6f42c1",
              ],
            },
          ],
        },
      });

      const resSamples = data.resolution.samples;
      new Chart(document.getElementById("resolutionChart"), {
        type: "line",
        data: {
          labels: resSamples.map((_, i) => i + 1),
          datasets: [
            {
              label: "Resolution time (days)",
              data: resSamples,
              fill: false,
              borderColor: "#198754",
            },
          ],
        },
      });
    })
    .catch((err) => {
      console.error("Error loading analytics", err);
    });
});


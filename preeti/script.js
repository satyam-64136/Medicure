document.addEventListener("DOMContentLoaded", () => {
  const medicineList = [
    { name: "Paracetamol", qty: 20, expiry: "2025-01-01", category: "Painkiller", price: 10 },
    { name: "Amoxicillin", qty: 5, expiry: "2024-12-15", category: "Antibiotic", price: 25 },
    { name: "Cough Syrup", qty: 12, expiry: "2025-03-10", category: "Syrup", price: 15 },
  ];

  const tableBody = document.getElementById("medicineList");
  const chartCtx = document.getElementById("stockChart").getContext("2d");
  let stockChart;

  function renderTable() {
    tableBody.innerHTML = "";
    medicineList.forEach((med, index) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${med.name}</td>
        <td>${med.qty}</td>
        <td>${med.expiry}</td>
        <td>${med.category}</td>
        <td>$${med.price}</td>
        <td>
          <button onclick="editMedicine(${index})">Edit</button>
          <button onclick="deleteMedicine(${index})">Delete</button>
        </td>
      `;
      tableBody.appendChild(row);
    });
    renderChart();
  }

  function renderChart() {
    const labels = medicineList.map(m => m.name);
    const data = medicineList.map(m => m.qty);
    const backgroundColors = data.map(qty => {
      if (qty > 70) return "green";
      if (qty >= 30) return "yellow";
      return "red";
    });

    if (stockChart) stockChart.destroy();

    stockChart = new Chart(chartCtx, {
      type: "pie",
      data: {
        labels,
        datasets: [{
          label: "Stock Level",
          data,
          backgroundColor: backgroundColors,
        }],
      },
    });
  }

  document.getElementById("searchBar").addEventListener("input", (e) => {
    const search = e.target.value.toLowerCase();
    const filtered = medicineList.filter(m => m.name.toLowerCase().includes(search));
    tableBody.innerHTML = "";
    filtered.forEach((med, index) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${med.name}</td>
        <td>${med.qty}</td>
        <td>${med.expiry}</td>
        <td>${med.category}</td>
        <td>$${med.price}</td>
        <td>
          <button onclick="editMedicine(${index})">Edit</button>
          <button onclick="deleteMedicine(${index})">Delete</button>
        </td>
      `;
      tableBody.appendChild(row);
    });
  });

  // You can expand this with modal open/edit/delete logic

  renderTable();
});

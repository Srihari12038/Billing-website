document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector(".sidebar");
  document.querySelector("[data-sidebar-toggle]")?.addEventListener("click", () => sidebar?.classList.toggle("open"));
  const currentPath = window.location.pathname;
  document.querySelectorAll(".sidebar nav a").forEach(link => {
    const linkPath = new URL(link.href, window.location.origin).pathname;
    const isDashboard = linkPath === "/" && currentPath === "/";
    const isSection = linkPath !== "/" && currentPath.startsWith(linkPath);
    if (isDashboard || isSection) link.classList.add("active");
  });
  document.querySelector("[data-check-all]")?.addEventListener("change", event => {
    document.querySelectorAll('input[name="ids"]').forEach(input => input.checked = event.target.checked);
  });
  const themeToggle = document.getElementById("themeToggle");
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") document.body.classList.add("dark");
  const syncThemeIcon = () => {
    const icon = themeToggle?.querySelector("i");
    if (icon) icon.className = document.body.classList.contains("dark") ? "bi bi-sun" : "bi bi-moon-stars";
  };
  syncThemeIcon();
  themeToggle?.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    localStorage.setItem("theme", document.body.classList.contains("dark") ? "dark" : "light");
    syncThemeIcon();
  });
  const chartCanvas = document.getElementById("salesExpenseChart");
  if (chartCanvas && window.Chart) {
    const labels = JSON.parse(document.getElementById("chart-labels").textContent);
    const sales = JSON.parse(document.getElementById("sales-data").textContent);
    const expenses = JSON.parse(document.getElementById("expense-data").textContent);
    new Chart(chartCanvas, {
      type: "line",
      data: {labels, datasets: [{label: "Sales", data: sales, borderColor: "#16A34A", backgroundColor: "rgba(22,163,74,.12)", tension: .35, fill: true}, {label: "Expenses", data: expenses, borderColor: "#F59E0B", backgroundColor: "rgba(245,158,11,.12)", tension: .35, fill: true}]},
      options: {responsive: true, plugins: {legend: {position: "bottom"}}, scales: {y: {beginAtZero: true}}}
    });
  }
  document.querySelectorAll(".invoice-items input[name$='-product_code']").forEach(input => {
    input.addEventListener("change", async () => {
      const code = input.value.trim();
      const row = input.closest("tr");
      const nameTarget = row?.querySelector(".product-name");
      if (!code || !window.productLookupUrl || !row) return;
      if (nameTarget) nameTarget.textContent = "Checking...";
      try {
        const response = await fetch(`${window.productLookupUrl}?code=${encodeURIComponent(code)}`);
        if (!response.ok) throw new Error("not found");
        const product = await response.json();
        row.querySelector("input[name$='-product']").value = product.id;
        row.querySelector("input[name$='-unit_price']").value = product.unit_price;
        row.querySelector("input[name$='-gst_rate']").value = product.gst_rate;
        if (nameTarget) nameTarget.textContent = `${product.name} | Stock ${product.stock}`;
      } catch (error) {
        row.querySelector("input[name$='-product']").value = "";
        if (nameTarget) nameTarget.textContent = "Product code not found";
      }
    });
  });
});

// frontend/api.js
// Put this file into frontend/ and include it in ALL HTML pages after Chart.js and before page scripts.

(function (global) {
  global.API_BASE = global.API_BASE || "http://localhost:5001";

  async function apiGet(path) {
    const res = await fetch(global.API_BASE + path, { credentials: "include" });
    if (!res.ok) throw new Error("API GET failed " + res.status);
    return res.json();
  }

  async function apiPost(path, body) {
    const res = await fetch(global.API_BASE + path, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error("API POST failed " + res.status);
    return res.json();
  }

  // Expose helpers
  global.ft = global.ft || {};
  global.ft.apiGet = apiGet;
  global.ft.apiPost = apiPost;

  // Chart helpers (to be called from pages)
  global.ft.initEmptyCharts = function () {
    try{
      const data=fetch(global.API_BASE+"/api/expenses/categories");
      console.log(data);
    }catch(err){  
      console.log("API not reachable");}
    // Expenses chart
    const expEl = document.getElementById("expensesChart");
    if (expEl && typeof Chart !== "undefined") {
      window.expensesChartInstance = new Chart(expEl.getContext("2d"), {
        type: "doughnut",
         
        data: { labels: [], datasets: [{ data: [] }] },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: "bottom" } },
        },
      });
    }

    // Income vs Expenses
    const ieEl = document.getElementById("incomeExpenseChart");
    if (ieEl && typeof Chart !== "undefined") {
      window.incomeExpenseChartInstance = new Chart(ieEl.getContext("2d"), {
        type: "bar",
        data: {
          labels: [],
          datasets: [
            { label: "Income", data: [] },
            { label: "Expenses", data: [] },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { beginAtZero: true } },
        },
      });
    }
  };

  // Dashboard loader
  global.ft.loadDashboard = async function (userId = 1) {
    try {
      const s = await apiGet(`/api/dashboard?user_id=${userId}`);
      if (s) {
        if (document.getElementById("totalBalance"))
          document.getElementById("totalBalance").textContent = `$${Number(
            s.totalBalance || 0
          ).toLocaleString()}`;
        if (document.getElementById("monthlyIncome"))
          document.getElementById("monthlyIncome").textContent = `$${Number(
            s.monthlyIncome || 0
          ).toLocaleString()}`;
        if (document.getElementById("monthlyExpenses"))
          document.getElementById("monthlyExpenses").textContent = `$${Number(
            s.monthlyExpenses || 0
          ).toLocaleString()}`;
        if (document.getElementById("remainingBudget"))
          document.getElementById("remainingBudget").textContent = `$${Number(
            s.remainingBudget || 0
          ).toLocaleString()}`;
      }

      const cats = await apiGet(`/api/expenses/categories?user_id=${userId}`);
      if (cats && window.expensesChartInstance) {
        window.expensesChartInstance.data.labels = cats.map((r) => r.category);
        window.expensesChartInstance.data.datasets = [
          { data: cats.map((r) => Number(r.total)) },
        ];
        window.expensesChartInstance.update();
      }

      const series = await apiGet(`/api/series/monthly?user_id=${userId}`);
      if (series && window.incomeExpenseChartInstance) {
        window.incomeExpenseChartInstance.data.labels = series.labels || [];
        window.incomeExpenseChartInstance.data.datasets[0].data =
          series.income || [];
        window.incomeExpenseChartInstance.data.datasets[1].data =
          series.expenses || [];
        window.incomeExpenseChartInstance.update();
      }
    } catch (err) {
      console.error("ft.loadDashboard error:", err);
    }
  };

  // Transactions loader for transactions page
  global.ft.loadTransactions = async function (userId = 1) {
    try {
      const txs = await apiGet(`/api/transactions?user_id=${userId}`);
      if (
        Array.isArray(txs) &&
        document.querySelector("#transactionsTable tbody")
      ) {
        const tbody = document.querySelector("#transactionsTable tbody");
        tbody.innerHTML = "";
        txs.forEach((tx) => {
          const tr = document.createElement("tr");
          tr.innerHTML = `<td>${tx.date}</td><td>${tx.description}</td><td>${
            tx.category
          }</td><td style="color:${tx.amount < 0 ? "#e74c3c" : "#27ae60"}">${
            tx.amount < 0 ? "-" : ""
          }$${Math.abs(tx.amount).toFixed(2)}</td><td>${tx.type}</td>`;
          tbody.appendChild(tr);
        });
      }
    } catch (err) {
      console.error("ft.loadTransactions error:", err);
    }
  };
})(window);

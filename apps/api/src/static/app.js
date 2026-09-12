let isLoginMode = true;
let authToken = localStorage.getItem("token") || null;
let currentAccountId = null;

const authSection = document.getElementById("auth-section");
const dashboardSection = document.getElementById("dashboard-section");
const userPill = document.getElementById("user-pill");
const userEmail = document.getElementById("user-email");
const authForm = document.getElementById("auth-form");
const authSubmit = document.getElementById("auth-submit");
const toast = document.getElementById("toast");
const depositBtn = document.getElementById("deposit-btn");
const createWalletBtn = document.getElementById("create-wallet-btn");

// Tab Switching
document.getElementById("tab-login").addEventListener("click", (e) => setAuthMode(true, e.target));
document.getElementById("tab-register").addEventListener("click", (e) => setAuthMode(false, e.target));

function setAuthMode(isLogin, element) {
  isLoginMode = isLogin;
  document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
  element.classList.add("active");
  authSubmit.innerText = isLogin ? "Sign In" : "Create Account";
}

// Toast System
function showToast(message, type = "success") {
  toast.innerText = message;
  toast.className = `toast ${type}`;
  setTimeout(() => toast.classList.add("hidden"), 3000);
}

// Auth Submit Listener
authForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("auth-email").value;
  const password = document.getElementById("auth-password").value;

  try {
    if (isLoginMode) {
      const body = new URLSearchParams({ username: email, password: password });
      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");
      
      authToken = data.access_token;
      localStorage.setItem("token", authToken);
      showToast("Signed in successfully!");
      initApp();
    } else {
      const res = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Registration failed");
      
      showToast("Registered! You can now sign in.", "success");
      setAuthMode(true, document.getElementById("tab-login"));
    }
  } catch (err) {
    showToast(err.message, "error");
  }
});

// Load User Accounts & Display Precise Balance
async function loadAccounts() {
  try {
    const res = await fetch("/api/v1/ledger/accounts/me", {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    const accounts = await res.json();
    if (accounts.length > 0) {
      const wallet = accounts[0];
      currentAccountId = wallet.id;
      
      // Fixed 2-decimal point precision formatting
      const formattedBalance = Number(wallet.balance).toFixed(2);
      document.getElementById("account-balance").innerText = formattedBalance;
      document.getElementById("account-id").innerText = wallet.id;
      document.getElementById("transfer-from").value = wallet.id;
      
      createWalletBtn.classList.add("hidden");
      depositBtn.classList.remove("hidden");
      loadTransactions(wallet.id);
    }
  } catch (err) {
    console.error(err);
  }
}

// Create Initial Wallet
createWalletBtn.addEventListener("click", async () => {
  try {
    const res = await fetch("/api/v1/ledger/accounts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${authToken}`
      },
      body: JSON.stringify({ currency: "USD" })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Could not create wallet");
    
    showToast("Wallet initialized!");
    loadAccounts();
  } catch (err) {
    showToast(err.message, "error");
  }
});

// Deposit $250.00 with Decimal String Precision
depositBtn.addEventListener("click", async () => {
  if (!currentAccountId) return;
  try {
    const res = await fetch("/api/v1/ledger/deposit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${authToken}`
      },
      body: JSON.stringify({ account_id: currentAccountId, amount: "250.00" })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Deposit failed");

    document.getElementById("account-balance").innerText = Number(data.balance).toFixed(2);
    showToast("Deposited $250.00 into wallet!");
    await loadAccounts();
  } catch (err) {
    showToast(err.message, "error");
  }
});

// Transfer Funds with Strict Decimal Precision & Instant PostgreSQL Sync
document.getElementById("transfer-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const rawAmount = document.getElementById("transfer-amount").value;
  
  const payload = {
    from_account_id: document.getElementById("transfer-from").value,
    to_account_id: document.getElementById("transfer-to").value,
    amount: Number(rawAmount).toFixed(2)
  };

  try {
    const res = await fetch("/api/v1/ledger/transfer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${authToken}`
      },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Transfer failed");

    showToast("Transfer executed successfully!");
    document.getElementById("transfer-amount").value = "";
    
    // Refresh state directly from database
    await loadAccounts();
  } catch (err) {
    showToast(err.message, "error");
  }
});

// Render Recent Activity Feed
async function loadTransactions(accId) {
  try {
    const res = await fetch(`/api/v1/ledger/transactions/${accId}`, {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    const txs = await res.json();
    const tbody = document.getElementById("tx-history-body");
    
    if (txs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="empty-state">No transactions yet</td></tr>`;
      return;
    }

    tbody.innerHTML = txs.map(tx => {
      const isOut = tx.from_account_id === accId;
      const typeLabel = isOut ? "Sent Transfer" : "Received Transfer";
      const amountClass = isOut ? "badge-out" : "badge-in";
      const prefix = isOut ? "-" : "+";

      return `
        <tr>
          <td>${typeLabel}</td>
          <td><code style="font-size:0.75rem">${tx.id.substring(0, 8)}...</code></td>
          <td class="${amountClass}">${prefix}$${Number(tx.amount).toFixed(2)}</td>
          <td><span class="badge-success">${tx.status}</span></td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    console.error(err);
  }
}

// Logout Listener
document.getElementById("logout-btn").addEventListener("click", () => {
  localStorage.removeItem("token");
  authToken = null;
  location.reload();
});

// App Initialization
async function initApp() {
  if (!authToken) return;
  try {
    const res = await fetch("/api/v1/auth/me", {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    if (!res.ok) throw new Error("Session expired");
    const user = await res.json();

    userEmail.innerText = user.email;
    authSection.classList.add("hidden");
    dashboardSection.classList.remove("hidden");
    userPill.classList.remove("hidden");

    loadAccounts();
  } catch (err) {
    localStorage.removeItem("token");
    authToken = null;
  }
}

initApp();
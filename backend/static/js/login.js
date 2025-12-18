const container = document.getElementById("container");

/* ================= TOGGLE ================= */

function showRegister() {
  container.classList.add("register-active");
}

function showLogin() {
  container.classList.remove("register-active");
}

/* ================= REGISTER ================= */

const registerForm = document.getElementById("registerForm");
const regUser = document.getElementById("regUser");
const regPass = document.getElementById("regPass");

registerForm.addEventListener("submit", async e => {
  e.preventDefault();

  const username = regUser.value.trim();
  const password = regPass.value.trim();

  if (!username || !password) {
    alert("Please fill all fields");
    return;
  }

  const res = await fetch("/api/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();

  if (data.message) {
    alert("Registration successful");
    showLogin();
    registerForm.reset();
  } else {
    alert(data.error || "Registration failed");
  }
});

/* ================= LOGIN ================= */

const loginForm = document.getElementById("loginForm");
const loginUser = document.getElementById("loginUser");
const loginPass = document.getElementById("loginPass");

loginForm.addEventListener("submit", async e => {
  e.preventDefault();

  const username = loginUser.value.trim();
  const password = loginPass.value.trim();

  if (!username || !password) {
    alert("Enter username and password");
    return;
  }

  const res = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();

  if (data.message) {
    window.location.href = "/dashboard";
  } else {
    alert(data.error || "Invalid credentials");
  }
});

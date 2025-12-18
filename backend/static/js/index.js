/* ===============================
   PROFILE MENU
=============================== */

const profileBtn = document.getElementById("profileBtn");
const profileMenu = document.getElementById("profileMenu");

if (profileBtn && profileMenu) {
    profileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        profileMenu.style.display =
            profileMenu.style.display === "block" ? "none" : "block";
    });

    document.addEventListener("click", (e) => {
        if (!profileBtn.contains(e.target) && !profileMenu.contains(e.target)) {
            profileMenu.style.display = "none";
        }
    });
}

/* ===============================
   THEME HANDLING (FIXED)
=============================== */

const root = document.documentElement;

const themes = {
    dark: {
        "--bg-color": "#0f172a",
        "--card-bg": "#1b2541",
        "--card-border": "#334155",
        "--text-color": "#f1f5f9",
        "--text-secondary": "#94a3b8",
        "--accent": "#818cf8",
        "--accent-strong": "#6366f1",
        "--success": "#22c55e",
        "--error": "#f87171"
    },

    light: {
        "--bg-color": "#f8fafc",
        "--card-bg": "#ffffff",
        "--card-border": "#e2e8f0",
        "--text-color": "#0f172a",
        "--text-secondary": "#475569",
        "--accent": "#6366f1",
        "--accent-strong": "#4f46e5",
        "--success": "#16a34a",
        "--error": "#dc2626"
    },

    yellow: {
        "--bg-color": "#fefce8",
        "--card-bg": "#fef3c7",
        "--card-border": "#fde68a",
        "--text-color": "#713f12",
        "--text-secondary": "#854d0e",
        "--accent": "#ca8a04",
        "--accent-strong": "#a16207",
        "--success": "#15803d",
        "--error": "#b91c1c"
    }
};

document.querySelectorAll(".theme-submenu li").forEach(item => {
    item.addEventListener("click", () => {
        const theme = item.dataset.theme;
        if (!themes[theme]) return;

        Object.entries(themes[theme]).forEach(([key, value]) => {
            root.style.setProperty(key, value);
        });

        localStorage.setItem("theme", theme);
    });
});

/* Load saved theme */
const savedTheme = localStorage.getItem("theme");
if (savedTheme && themes[savedTheme]) {
    Object.entries(themes[savedTheme]).forEach(([key, value]) => {
        root.style.setProperty(key, value);
    });
}

/* ===============================
   🚀 LAUNCH TOOL HANDLER
=============================== */

document.querySelectorAll(".launch").forEach(btn => {
    btn.addEventListener("click", () => {
        const tool = btn.dataset.tool;

        if (!tool) {
            alert("Tool not found");
            return;
        }

        const routes = {
            video: "/video",
            web: "/web",
            voice: "/voice",
            pdf: "/pdf",
            code: "/code"
        };

        if (routes[tool]) {
            window.location.href = routes[tool];
        } else {
            alert("Tool not available");
        }
    });
});

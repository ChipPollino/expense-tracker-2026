import { apiRequest, showToast, setButtonLoading } from "./api.js";

const state = {
    user: null,
    settings: null,
    categories: [],
    expenses: [],
    summary: null,
    monthSummary: null,
    byCategory: [],
    monthly: [],
    charts: { category: null, monthly: null },
};

const sectionMeta = {
    dashboard: ["Финансовый обзор", "Добрый день"],
    expenses: ["История операций", "Расходы"],
    categories: ["Группировка", "Категории"],
    settings: ["Персонализация", "Настройки"],
    profile: ["Аккаунт", "Профиль"],
};

const money = new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 2,
});
const dateTime = new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
});

const q = (selector, root = document) => root.querySelector(selector);
const qa = (selector, root = document) => [...root.querySelectorAll(selector)];

function formatMoney(value) {
    return money.format(Number(value || 0));
}

function formatDate(value) {
    return value ? dateTime.format(new Date(value)) : "—";
}

function toIso(value) {
    return value ? new Date(value).toISOString() : undefined;
}

function toLocalInputValue(value = new Date()) {
    const date = new Date(value);
    const offset = date.getTimezoneOffset();
    return new Date(date.getTime() - offset * 60_000).toISOString().slice(0, 16);
}

function currentMonthStartIso() {
    const now = new Date();
    return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 1)).toISOString();
}

function applyTheme(theme) {
    const normalized = theme === "dark" ? "dark" : "light";
    document.documentElement.dataset.theme = normalized;
    localStorage.setItem("expense-tracker-theme", normalized);
}

function redirectToLogin() {
    window.location.href = "/login";
}

async function safeRequest(path, options = {}) {
    try {
        return await apiRequest(path, options);
    } catch (error) {
        if (error.status === 401) {
            redirectToLogin();
            return null;
        }
        throw error;
    }
}

async function loadProfile() {
    state.user = await safeRequest("/users/me");
}

async function loadSettings() {
    state.settings = await safeRequest("/settings");
    if (state.settings) applyTheme(state.settings.theme);
}

async function loadCategories() {
    state.categories = await safeRequest("/categories") || [];
}

async function loadExpenses(query = "") {
    state.expenses = await safeRequest(`/expenses${query}`) || [];
}

async function loadAnalytics() {
    const monthQuery = new URLSearchParams({ date_from: currentMonthStartIso() });
    [state.summary, state.monthSummary, state.byCategory, state.monthly] = await Promise.all([
        safeRequest("/analytics/summary"),
        safeRequest(`/analytics/summary?${monthQuery}`),
        safeRequest("/analytics/by-category"),
        safeRequest("/analytics/monthly"),
    ]);
}

function renderProfile() {
    if (!state.user) return;
    q("#user-name").textContent = state.user.name;
    q("#user-email").textContent = state.user.email;
    q("#user-avatar").textContent = state.user.name.trim().slice(0, 1).toUpperCase() || "?";
    q("#profile-name").value = state.user.name;
    q("#profile-email").value = state.user.email;
}

function renderSettings() {
    if (!state.settings) return;
    q("#theme-select").value = state.settings.theme;
    q("#monthly-limit").value = state.settings.monthly_limit ?? "";
}

function renderCategoryOptions() {
    const filterSelect = q("#filter-category");
    const expenseSelect = q("#expense-category");
    const options = state.categories
        .map((category) => `<option value="${category.id}">${escapeHtml(category.name)}</option>`)
        .join("");

    filterSelect.innerHTML = `<option value="">Все категории</option>${options}`;
    expenseSelect.innerHTML = options || `<option value="">Сначала создайте категорию</option>`;
}

function renderCategories() {
    q("#categories-count").textContent = state.categories.length;
    const list = q("#category-list");
    const empty = q("#categories-empty");

    if (!state.categories.length) {
        list.innerHTML = "";
        empty.classList.remove("is-hidden");
        return;
    }

    empty.classList.add("is-hidden");
    list.innerHTML = state.categories.map((category) => `
        <div class="category-item">
            <div class="category-item__main">
                <span class="category-item__dot"></span>
                <strong>${escapeHtml(category.name)}</strong>
            </div>
            <div class="row-actions">
                <button class="row-action" type="button" data-edit-category="${category.id}">Изменить</button>
                <button class="row-action row-action--danger" type="button" data-delete-category="${category.id}">Удалить</button>
            </div>
        </div>
    `).join("");
}

function expenseRow(expense, withActions = true) {
    return `
        <tr>
            <td><span class="category-badge">${escapeHtml(expense.category)}</span></td>
            <td>${escapeHtml(expense.description || "Без описания")}</td>
            <td>${formatDate(expense.expense_date)}</td>
            <td class="table-number"><strong>${formatMoney(expense.amount)}</strong></td>
            ${withActions ? `
            <td class="table-actions">
                <div class="row-actions">
                    <button class="row-action" type="button" data-edit-expense="${expense.id}">Изменить</button>
                    <button class="row-action row-action--danger" type="button" data-delete-expense="${expense.id}">×</button>
                </div>
            </td>` : ""}
        </tr>`;
}

function renderExpenses() {
    const body = q("#expenses-body");
    const recentBody = q("#recent-expenses-body");
    const empty = q("#expenses-empty");
    const recentEmpty = q("#recent-expenses-empty");

    body.innerHTML = state.expenses.map((expense) => expenseRow(expense)).join("");
    empty.classList.toggle("is-hidden", state.expenses.length > 0);

    const recent = state.expenses.slice(0, 5);
    recentBody.innerHTML = recent.map((expense) => expenseRow(expense, false)).join("");
    recentEmpty.classList.toggle("is-hidden", recent.length > 0);

    const latest = state.expenses[0];
    q("#latest-expense").textContent = latest ? formatMoney(latest.amount) : "—";
    q("#latest-expense-caption").textContent = latest
        ? `${latest.category} · ${formatDate(latest.expense_date)}`
        : "Пока данных нет";
}

function renderDashboardMetrics() {
    q("#summary-total").textContent = formatMoney(state.summary?.total || 0);
    q("#summary-count").textContent = `${state.summary?.expenses_count || 0} операций за все время`;

    const limit = state.settings?.monthly_limit;
    const spent = Number(state.monthSummary?.total || 0);
    const caption = q("#budget-caption");
    const progress = q("#budget-progress");

    if (limit === null || limit === undefined) {
        q("#budget-limit").textContent = "Не задан";
        caption.textContent = "Можно установить в настройках";
        progress.style.width = "0%";
        return;
    }

    const numericLimit = Number(limit);
    const percent = numericLimit === 0 ? (spent > 0 ? 100 : 0) : Math.min((spent / numericLimit) * 100, 100);
    q("#budget-limit").textContent = formatMoney(limit);
    caption.textContent = `${formatMoney(spent)} потрачено в этом месяце`;
    progress.style.width = `${percent}%`;
}

function chartTextColor() {
    return getComputedStyle(document.documentElement).getPropertyValue("--muted").trim();
}

function chartGridColor() {
    return getComputedStyle(document.documentElement).getPropertyValue("--line").trim();
}

function renderCharts() {
    const categoryEmpty = q("#category-chart-empty");
    const monthlyEmpty = q("#monthly-chart-empty");

    state.charts.category?.destroy();
    state.charts.monthly?.destroy();

    categoryEmpty.classList.toggle("is-hidden", state.byCategory.length > 0);
    monthlyEmpty.classList.toggle("is-hidden", state.monthly.length > 0);

    if (state.byCategory.length) {
        state.charts.category = new Chart(q("#category-chart"), {
            type: "doughnut",
            data: {
                labels: state.byCategory.map((item) => item.category),
                datasets: [{ data: state.byCategory.map((item) => Number(item.total)), borderWidth: 0 }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "68%",
                plugins: { legend: { position: "bottom", labels: { color: chartTextColor(), boxWidth: 10, usePointStyle: true, padding: 16 } } },
            },
        });
    }

    if (state.monthly.length) {
        state.charts.monthly = new Chart(q("#monthly-chart"), {
            type: "line",
            data: {
                labels: state.monthly.map((item) => item.month),
                datasets: [{ label: "Расходы", data: state.monthly.map((item) => Number(item.total)), tension: .36, fill: true }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: chartTextColor() }, grid: { display: false } },
                    y: { beginAtZero: true, ticks: { color: chartTextColor(), callback: (value) => `${value} ₽` }, grid: { color: chartGridColor() } },
                },
            },
        });
    }
}

function renderAll() {
    renderProfile();
    renderSettings();
    renderCategoryOptions();
    renderCategories();
    renderExpenses();
    renderDashboardMetrics();
    renderCharts();
}

function switchSection(section) {
    if (!sectionMeta[section]) return;
    qa("[data-page]").forEach((page) => page.classList.toggle("is-active", page.dataset.page === section));
    qa("[data-section]").forEach((button) => button.classList.toggle("is-active", button.dataset.section === section));
    q("#section-eyebrow").textContent = sectionMeta[section][0];
    q("#section-title").textContent = sectionMeta[section][1];
    q("#sidebar").classList.remove("is-open");
}

function openExpenseModal(expense = null) {
    if (!state.categories.length) {
        showToast("Сначала создайте хотя бы одну категорию", "error");
        switchSection("categories");
        return;
    }

    const modal = q("#expense-modal");
    q("#expense-form").reset();
    q("#expense-id").value = expense?.id || "";
    q("#expense-modal-title").textContent = expense ? "Изменить трату" : "Новая трата";
    q("#expense-date").value = toLocalInputValue(expense?.expense_date || new Date());

    if (expense) {
        const category = state.categories.find((item) => item.name === expense.category);
        q("#expense-category").value = category?.id || "";
        q("#expense-amount").value = expense.amount;
        q("#expense-description").value = expense.description || "";
    }

    modal.showModal();
}

function closeExpenseModal() {
    q("#expense-modal").close();
}

function buildExpensePayload(form) {
    const raw = new FormData(form);
    const payload = {
        category_id: Number(raw.get("category_id")),
        amount: Number(raw.get("amount")),
        description: raw.get("description")?.trim() || null,
    };
    const date = toIso(raw.get("expense_date"));
    if (date) payload.expense_date = date;
    return payload;
}

async function refreshFinancialData() {
    await Promise.all([loadExpenses(), loadAnalytics()]);
    renderExpenses();
    renderDashboardMetrics();
    renderCharts();
}

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (char) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#039;", '"': "&quot;",
    })[char]);
}

function bindNavigation() {
    qa("[data-section]").forEach((button) => button.addEventListener("click", () => switchSection(button.dataset.section)));
    qa("[data-section-jump]").forEach((button) => button.addEventListener("click", () => switchSection(button.dataset.sectionJump)));
    q("#mobile-menu").addEventListener("click", () => q("#sidebar").classList.toggle("is-open"));
}

function bindAuthActions() {
    q("#logout-button").addEventListener("click", async () => {
        try {
            await apiRequest("/auth/logout", { method: "POST" });
        } finally {
            redirectToLogin();
        }
    });
}

function bindExpenseActions() {
    qa("[data-open-expense-modal]").forEach((button) => button.addEventListener("click", () => openExpenseModal()));
    qa("[data-close-modal]").forEach((button) => button.addEventListener("click", closeExpenseModal));

    q("#expense-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const id = q("#expense-id").value;
        const button = q("#expense-form button[type='submit']");

        try {
            setButtonLoading(button, true, "Сохраняем...");
            await safeRequest(id ? `/expenses/${id}` : "/expenses", {
                method: id ? "PATCH" : "POST",
                body: buildExpensePayload(event.currentTarget),
            });
            closeExpenseModal();
            await refreshFinancialData();
            showToast(id ? "Трата обновлена" : "Трата добавлена");
        } catch (error) {
            showToast(error.message, "error");
        } finally {
            setButtonLoading(button, false);
        }
    });

    q("#expenses-body").addEventListener("click", async (event) => {
        const edit = event.target.closest("[data-edit-expense]");
        const remove = event.target.closest("[data-delete-expense]");

        if (edit) {
            const expense = state.expenses.find((item) => String(item.id) === edit.dataset.editExpense);
            if (expense) openExpenseModal(expense);
        }

        if (remove && confirm("Удалить эту трату?")) {
            try {
                await safeRequest(`/expenses/${remove.dataset.deleteExpense}`, { method: "DELETE" });
                await refreshFinancialData();
                showToast("Трата удалена");
            } catch (error) {
                showToast(error.message, "error");
            }
        }
    });

    q("#expense-filter-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const params = new URLSearchParams();
        new FormData(event.currentTarget).forEach((value, key) => {
            if (!value) return;
            params.set(key, ["date_from", "date_to"].includes(key) ? toIso(value) : value);
        });
        try {
            await loadExpenses(params.toString() ? `?${params}` : "");
            renderExpenses();
        } catch (error) {
            showToast(error.message, "error");
        }
    });

    q("#reset-filters").addEventListener("click", async () => {
        window.setTimeout(async () => {
            await loadExpenses();
            renderExpenses();
        }, 0);
    });
}

function bindCategoryActions() {
    q("#category-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const button = q("#category-form button[type='submit']");
        const name = new FormData(event.currentTarget).get("name");
        try {
            setButtonLoading(button, true, "Создаем...");
            await safeRequest("/categories", { method: "POST", body: { name } });
            event.currentTarget.reset();
            await loadCategories();
            renderCategoryOptions();
            renderCategories();
            showToast("Категория создана");
        } catch (error) {
            showToast(error.message, "error");
        } finally {
            setButtonLoading(button, false);
        }
    });

    q("#category-list").addEventListener("click", async (event) => {
        const edit = event.target.closest("[data-edit-category]");
        const remove = event.target.closest("[data-delete-category]");

        if (edit) {
            const category = state.categories.find((item) => String(item.id) === edit.dataset.editCategory);
            const name = prompt("Новое название категории", category?.name || "");
            if (!name || name === category?.name) return;
            try {
                await safeRequest(`/categories/${edit.dataset.editCategory}`, { method: "PATCH", body: { name } });
                await Promise.all([loadCategories(), loadExpenses(), loadAnalytics()]);
                renderAll();
                showToast("Категория обновлена");
            } catch (error) {
                showToast(error.message, "error");
            }
        }

        if (remove && confirm("Удалить категорию? Категорию с расходами удалить нельзя.")) {
            try {
                await safeRequest(`/categories/${remove.dataset.deleteCategory}`, { method: "DELETE" });
                await loadCategories();
                renderCategoryOptions();
                renderCategories();
                showToast("Категория удалена");
            } catch (error) {
                showToast(error.message, "error");
            }
        }
    });
}

function bindSettingsActions() {
    q("#settings-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const button = q("#settings-form button[type='submit']");
        const raw = new FormData(event.currentTarget);
        const limit = raw.get("monthly_limit");
        try {
            setButtonLoading(button, true, "Сохраняем...");
            state.settings = await safeRequest("/settings", {
                method: "PATCH",
                body: { theme: raw.get("theme"), monthly_limit: limit === "" ? null : Number(limit) },
            });
            applyTheme(state.settings.theme);
            renderSettings();
            renderDashboardMetrics();
            renderCharts();
            showToast("Настройки сохранены");
        } catch (error) {
            showToast(error.message, "error");
        } finally {
            setButtonLoading(button, false);
        }
    });

    q("#reset-limit").addEventListener("click", async () => {
        try {
            state.settings = await safeRequest("/settings", { method: "PATCH", body: { monthly_limit: null } });
            renderSettings();
            renderDashboardMetrics();
            showToast("Месячный лимит сброшен");
        } catch (error) {
            showToast(error.message, "error");
        }
    });

    q("#sidebar-theme-toggle").addEventListener("click", async () => {
        const theme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
        try {
            state.settings = await safeRequest("/settings", { method: "PATCH", body: { theme } });
            applyTheme(theme);
            renderSettings();
            renderCharts();
        } catch (error) {
            showToast(error.message, "error");
        }
    });
}

function bindProfileActions() {
    q("#profile-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const button = q("#profile-form button[type='submit']");
        const raw = new FormData(event.currentTarget);
        try {
            setButtonLoading(button, true, "Сохраняем...");
            state.user = await safeRequest("/users/me", { method: "PATCH", body: { name: raw.get("name"), email: raw.get("email") } });
            renderProfile();
            showToast("Профиль обновлен");
        } catch (error) {
            showToast(error.message, "error");
        } finally {
            setButtonLoading(button, false);
        }
    });

    q("#password-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const button = q("#password-form button[type='submit']");
        const raw = new FormData(event.currentTarget);
        try {
            setButtonLoading(button, true, "Меняем пароль...");
            await safeRequest("/auth/change-password", { method: "PATCH", body: { old_password: raw.get("old_password"), new_password: raw.get("new_password") } });
            event.currentTarget.reset();
            showToast("Пароль изменен");
        } catch (error) {
            showToast(error.message, "error");
        } finally {
            setButtonLoading(button, false);
        }
    });

    q("#delete-account").addEventListener("click", async () => {
        const accepted = confirm("Удалить аккаунт навсегда? Это действие нельзя отменить.");
        if (!accepted) return;
        try {
            await safeRequest("/users/me", { method: "DELETE" });
            redirectToLogin();
        } catch (error) {
            showToast(error.message, "error");
        }
    });
}

async function init() {
    applyTheme(localStorage.getItem("expense-tracker-theme") || "light");
    bindNavigation();
    bindAuthActions();
    bindExpenseActions();
    bindCategoryActions();
    bindSettingsActions();
    bindProfileActions();

    try {
        await Promise.all([loadProfile(), loadSettings(), loadCategories()]);
        await Promise.all([loadExpenses(), loadAnalytics()]);
        renderAll();
    } catch (error) {
        showToast(error.message, "error");
    }
}

init();

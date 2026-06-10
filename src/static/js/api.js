export class ApiError extends Error {
    constructor(message, status = 0, details = null) {
        super(message);
        this.name = "ApiError";
        this.status = status;
        this.details = details;
    }
}

export async function apiRequest(path, options = {}) {
    const headers = new Headers(options.headers || {});
    const hasBody = options.body !== undefined && options.body !== null;

    if (hasBody && !(options.body instanceof FormData)) {
        headers.set("Content-Type", "application/json");
    }

    const response = await fetch(path, {
        credentials: "same-origin",
        ...options,
        headers,
        body: hasBody && !(options.body instanceof FormData)
            ? JSON.stringify(options.body)
            : options.body,
    });

    if (response.status === 204) {
        return null;
    }

    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json")
        ? await response.json()
        : await response.text();

    if (!response.ok) {
        const detail = typeof data === "object" && data !== null
            ? data.detail
            : data;
        const message = Array.isArray(detail)
            ? detail.map((item) => item.msg).join("; ")
            : detail || "Не удалось выполнить запрос";
        throw new ApiError(message, response.status, data);
    }

    return data;
}

export function showToast(message, type = "success") {
    const container = document.querySelector("#toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast${type === "error" ? " toast--error" : ""}`;
    toast.textContent = message;
    container.append(toast);

    window.setTimeout(() => toast.remove(), 3400);
}

export function setButtonLoading(button, isLoading, loadingText = "Подождите...") {
    if (!button) return;
    if (isLoading) {
        button.dataset.originalText = button.innerHTML;
        button.disabled = true;
        button.textContent = loadingText;
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || button.innerHTML;
    }
}

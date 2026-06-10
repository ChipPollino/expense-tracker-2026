import { apiRequest, showToast, setButtonLoading } from "./api.js";

const loginForm = document.querySelector("#login-form");
const registerForm = document.querySelector("#register-form");

if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const button = loginForm.querySelector("button[type='submit']");
        const form = new FormData(loginForm);

        try {
            setButtonLoading(button, true, "Входим...");
            await apiRequest("/auth/login", {
                method: "POST",
                body: {
                    email: form.get("email"),
                    password: form.get("password"),
                },
            });
            window.location.href = "/app";
        } catch (error) {
            showToast(error.message, "error");
        } finally {
            setButtonLoading(button, false);
        }
    });
}

if (registerForm) {
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const button = registerForm.querySelector("button[type='submit']");
        const form = new FormData(registerForm);

        try {
            setButtonLoading(button, true, "Создаем аккаунт...");
            await apiRequest("/auth/register", {
                method: "POST",
                body: {
                    name: form.get("name"),
                    email: form.get("email"),
                    password: form.get("password"),
                },
            });
            await apiRequest("/auth/login", {
                method: "POST",
                body: {
                    email: form.get("email"),
                    password: form.get("password"),
                },
            });
            window.location.href = "/app";
        } catch (error) {
            showToast(error.message, "error");
        } finally {
            setButtonLoading(button, false);
        }
    });
}

import { defineStore } from "pinia";
import { ref, computed } from "vue";
import router from "@/router";

export const useAuthStore = defineStore("auth", () => {
    // State
    const token = ref(localStorage.getItem("token") || null);
    const user = ref(JSON.parse(localStorage.getItem("user") || "null"));
    const salesperson = ref(
        JSON.parse(localStorage.getItem("salesperson") || "null")
    );
    const isAdmin = ref(JSON.parse(localStorage.getItem("isAdmin") || "false"));
    const loading = ref(false);
    const error = ref(null);

    // Getters
    const isAuthenticated = computed(() => !!token.value);
    const currentUser = computed(() => user.value);
    const currentSalesperson = computed(() => salesperson.value);
    const adminStatus = computed(() => isAdmin.value);

    // Actions
    const login = async (username, password) => {
        loading.value = true;
        error.value = null;

        try {
            const formData = new FormData();
            formData.append("username", username);
            formData.append("password", password);

            const response = await fetch("/api/login", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Login failed");
            }

            const data = await response.json();

            // Store token and user data
            token.value = data.access_token;
            user.value = { username };
            salesperson.value = data.salesperson || null;
            isAdmin.value = data.is_admin || false;

            // Persist to localStorage
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("user", JSON.stringify({ username }));
            localStorage.setItem(
                "isAdmin",
                JSON.stringify(data.is_admin || false)
            );
            if (data.salesperson) {
                localStorage.setItem(
                    "salesperson",
                    JSON.stringify(data.salesperson)
                );
            }

            return data;
        } catch (err) {
            error.value = err.message;
            throw err;
        } finally {
            loading.value = false;
        }
    };

    const logout = () => {
        token.value = null;
        user.value = null;
        salesperson.value = null;
        isAdmin.value = false;
        error.value = null;

        // Clear localStorage
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        localStorage.removeItem("salesperson");
        localStorage.removeItem("isAdmin");

        // Navigate to login page
        router.push("/login");
    };

    const clearError = () => {
        error.value = null;
    };

    // API helper with authentication
    const apiCall = async (url, options = {}) => {
        if (!token.value) {
            throw new Error("No authentication token");
        }

        const defaultOptions = {
            headers: {
                Authorization: `Bearer ${token.value}`,
                "Content-Type": "application/json",
                ...options.headers,
            },
        };

        const response = await fetch(url, { ...defaultOptions, ...options });

        if (response.status === 401) {
            // Token expired or invalid
            logout();
            throw new Error("Authentication expired");
        }

        return response;
    };

    return {
        // State
        token,
        user,
        salesperson,
        isAdmin,
        loading,
        error,

        // Getters
        isAuthenticated,
        currentUser,
        currentSalesperson,
        adminStatus,

        // Actions
        login,
        logout,
        clearError,
        apiCall,
    };
});

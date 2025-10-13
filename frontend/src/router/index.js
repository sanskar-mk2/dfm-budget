import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/",
            name: "sales",
            component: () => import("../views/SalesView.vue"),
            meta: { requiresAuth: true, requiresAdmin: false },
        },
        {
            path: "/admin",
            name: "admin",
            component: () => import("../views/AdminView.vue"),
            meta: { requiresAuth: true, requiresAdmin: true },
        },
        {
            path: "/salesperson/:salespersonId",
            name: "salesperson",
            component: () => import("../views/SalespersonView.vue"),
            meta: { requiresAuth: true, requiresAdmin: true },
        },
        {
            path: "/login",
            name: "login",
            component: () => import("../views/LoginView.vue"),
            meta: { requiresAuth: false },
        },
    ],
});

// Navigation guard
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();

    // Check authentication
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next("/login");
        return;
    }

    // Redirect from login if already authenticated
    if (to.name === "login" && authStore.isAuthenticated) {
        // Redirect admins to admin view, regular users to sales view
        next(authStore.adminStatus ? "/admin" : "/");
        return;
    }

    // Check admin requirements
    if (to.meta.requiresAdmin && !authStore.adminStatus) {
        // Non-admin trying to access admin route
        next("/");
        return;
    }

    // Check if admin is trying to access non-admin route
    if (
        to.meta.requiresAdmin === false &&
        authStore.adminStatus &&
        to.name === "sales"
    ) {
        // Admin trying to access sales view, redirect to admin
        next("/admin");
        return;
    }

    next();
});

export default router;

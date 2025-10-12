import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import HomeView from "../views/HomeView.vue";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/",
            name: "home",
            component: HomeView,
            meta: { requiresAuth: true },
        },
        {
            path: "/about",
            name: "about",
            component: () => import("../views/AboutView.vue"),
            meta: { requiresAuth: true },
        },
        {
            path: "/sales",
            name: "sales",
            component: () => import("../views/SalesView.vue"),
            meta: { requiresAuth: true },
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

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next("/login");
    } else if (to.name === "login" && authStore.isAuthenticated) {
        next("/");
    } else {
        next();
    }
});

export default router;

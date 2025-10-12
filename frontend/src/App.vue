<script setup>
import { RouterLink, RouterView } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { computed } from "vue";

const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);
</script>

<template>
    <div class="min-h-screen bg-base-100">
        <!-- Navigation Bar (only show when authenticated) -->
        <div v-if="isAuthenticated" class="navbar bg-base-200 shadow-lg">
            <div class="navbar-start">
                <div class="dropdown">
                    <div
                        tabindex="0"
                        role="button"
                        class="btn btn-ghost lg:hidden"
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-5 w-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M4 6h16M4 12h8m-8 6h16"
                            />
                        </svg>
                    </div>
                    <ul
                        tabindex="0"
                        class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52"
                    >
                        <li><RouterLink to="/">Home</RouterLink></li>
                        <li><RouterLink to="/about">About</RouterLink></li>
                        <li><RouterLink to="/sales">Sales</RouterLink></li>
                    </ul>
                </div>
                <RouterLink to="/" class="btn btn-ghost text-xl"
                    >Budget App</RouterLink
                >
            </div>

            <div class="navbar-center hidden lg:flex">
                <ul class="menu menu-horizontal px-1">
                    <li>
                        <RouterLink to="/" class="btn btn-ghost"
                            >Home</RouterLink
                        >
                    </li>
                    <li>
                        <RouterLink to="/about" class="btn btn-ghost"
                            >About</RouterLink
                        >
                    </li>
                    <li>
                        <RouterLink to="/sales" class="btn btn-ghost"
                            >Sales</RouterLink
                        >
                    </li>
                </ul>
            </div>

            <div class="navbar-end">
                <div class="dropdown dropdown-end">
                    <div
                        tabindex="0"
                        role="button"
                        class="btn btn-ghost btn-circle avatar"
                    >
                        <div
                            class="w-10 rounded-full bg-primary text-primary-content flex items-center justify-center"
                        >
                            <span class="text-sm font-bold">{{
                                authStore.currentUser?.username
                                    ?.charAt(0)
                                    .toUpperCase()
                            }}</span>
                        </div>
                    </div>
                    <ul
                        tabindex="0"
                        class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52"
                    >
                        <li>
                            <div class="text-sm">
                                <div class="font-bold">
                                    {{ authStore.currentUser?.username }}
                                </div>
                                <div
                                    v-if="authStore.currentSalesperson"
                                    class="text-xs opacity-70"
                                >
                                    {{ authStore.currentSalesperson.name }}
                                </div>
                            </div>
                        </li>
                        <li><hr class="my-1" /></li>
                        <li>
                            <button
                                @click="authStore.logout()"
                                class="text-error"
                            >
                                Logout
                            </button>
                        </li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <main>
            <RouterView />
        </main>
    </div>
</template>

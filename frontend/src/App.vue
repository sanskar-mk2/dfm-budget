<script setup>
import { RouterLink, RouterView } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { computed, ref, provide } from "vue";

const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);

// Modal state for custom budget
const isAddBudgetModalOpen = ref(false);

const openAddBudgetModal = () => {
    isAddBudgetModalOpen.value = true;
};

const closeAddBudgetModal = () => {
    isAddBudgetModalOpen.value = false;
};

// Provide modal state to child components
provide('addBudgetModal', {
    isOpen: isAddBudgetModalOpen,
    open: openAddBudgetModal,
    close: closeAddBudgetModal
});
</script>

<template>
    <div class="min-h-screen bg-base-100">
        <!-- Navigation Bar (only show when authenticated) -->
        <div v-if="isAuthenticated" class="navbar bg-base-200 shadow-lg">
            <div class="navbar-start">
                <RouterLink to="/" class="btn btn-ghost text-xl"
                    >Budget 2026</RouterLink
                >
            </div>

            <div class="navbar-end">
                <button @click="openAddBudgetModal" class="btn btn-primary mr-2">
                    Add Custom Budget
                </button>
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

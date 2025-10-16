<script setup>
import { RouterLink, RouterView, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { computed, ref, provide, watch } from "vue";

const authStore = useAuthStore();
const route = useRoute();
const isAuthenticated = computed(() => authStore.isAuthenticated);

// Check if current route is admin dashboard (not individual salesperson view)
const isAdminView = computed(() => route.name === "admin");

// Salesperson info for navbar display
const salespersonInfo = ref(null);
const loadingSalespersonInfo = ref(false);

// Fetch salesperson info when on salesperson route
const fetchSalespersonInfo = async (salespersonId) => {
    if (!salespersonId) return;

    loadingSalespersonInfo.value = true;
    try {
        const response = await authStore.apiCall(
            `/api/salesperson/${salespersonId}/info`
        );
        if (response.ok) {
            const data = await response.json();
            salespersonInfo.value = data.data;
        }
    } catch (error) {
        console.error("Error fetching salesperson info:", error);
    } finally {
        loadingSalespersonInfo.value = false;
    }
};

// Watch for route changes to fetch salesperson info
watch(
    () => route.params.salespersonId,
    (newId) => {
        if (route.name === "salesperson" && newId) {
            fetchSalespersonInfo(newId);
        } else {
            salespersonInfo.value = null;
        }
    },
    { immediate: true }
);

// Modal state for custom budget
const isAddBudgetModalOpen = ref(false);

const openAddBudgetModal = () => {
    isAddBudgetModalOpen.value = true;
};

const closeAddBudgetModal = () => {
    isAddBudgetModalOpen.value = false;
};

// Navigation actions state
const navActions = ref([]);

const setNavActions = (actions) => {
    navActions.value = actions;
};

const clearNavActions = () => {
    navActions.value = [];
};

// Provide modal state and navigation actions to child components
provide("addBudgetModal", {
    isOpen: isAddBudgetModalOpen,
    open: openAddBudgetModal,
    close: closeAddBudgetModal,
});

provide("navActions", {
    set: setNavActions,
    clear: clearNavActions,
    actions: navActions,
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

            <div class="navbar-center">
                <!-- Salesperson Info (only show on salesperson view) -->
                <div
                    v-if="route.name === 'salesperson'"
                    class="flex items-center gap-3"
                >
                    <div
                        v-if="loadingSalespersonInfo"
                        class="text-sm opacity-60"
                    >
                        <div class="font-semibold">Loading...</div>
                        <div class="text-xs">Salesperson Details</div>
                    </div>
                    <div v-else-if="salespersonInfo" class="text-sm">
                        <div class="font-semibold">
                            {{ salespersonInfo.salesperson_name }}
                        </div>
                        <div class="flex items-center gap-2 text-xs opacity-70">
                            <span
                                class="badge badge-sm"
                                :class="
                                    salespersonInfo.role === 'Hospitality'
                                        ? 'badge-primary'
                                        : 'badge-secondary'
                                "
                            >
                                {{ salespersonInfo.role }}
                            </span>
                            <span
                                >ID: {{ salespersonInfo.salesperson_id }}</span
                            >
                        </div>
                    </div>
                    <div v-else class="text-sm">
                        <div class="font-semibold">Salesperson View</div>
                        <div class="text-xs opacity-70">
                            ID: {{ route.params.salespersonId }}
                        </div>
                    </div>
                </div>
            </div>

            <div class="navbar-end">
                <button
                    v-if="route.name === 'salesperson' && authStore.adminStatus"
                    @click="openAddBudgetModal"
                    class="btn btn-primary mr-2"
                >
                    Add Custom Row
                </button>
                <!-- Dynamic navigation actions from views -->
                <template v-for="action in navActions" :key="action.id">
                    <button
                        v-if="action.condition !== false"
                        @click="action.handler"
                        :class="action.class || 'btn btn-primary mr-2'"
                        :disabled="action.disabled"
                        :title="action.title"
                    >
                        <svg
                            v-if="action.icon"
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-5 w-5 mr-2"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                            v-html="action.icon"
                        ></svg>
                        {{ action.text }}
                    </button>
                </template>
                <div class="dropdown dropdown-end">
                    <div tabindex="0" role="button" class="btn btn-ghost">
                        {{ authStore.currentUser?.username }}
                    </div>
                    <ul
                        tabindex="0"
                        class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52"
                    >
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

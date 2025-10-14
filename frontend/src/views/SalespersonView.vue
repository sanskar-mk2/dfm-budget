<template>
    <div class="mx-auto px-4 py-8">
        <!-- Loading State -->
        <div v-if="loading" class="flex justify-center">
            <div class="loading loading-spinner loading-lg"></div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-error">
            <svg
                xmlns="http://www.w3.org/2000/svg"
                class="stroke-current shrink-0 h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
            </svg>
            <span>{{ error }}</span>
        </div>

        <!-- Empty State -->
        <div v-else-if="sales.length === 0" class="text-center py-8">
            <p class="text-lg text-base-content/70">No sales data found</p>
        </div>

        <!-- Main Content -->
        <div v-else>
            <!-- Sales Table -->
            <SalesTable
                :sales="sales"
                :custom-budgets="getCustomBudgets()"
                :get-budget-value="getBudgetValue"
                :get-cell-class="getCellClass"
                :handle-budget-change="handleBudgetChange"
                :handle-budget-blur="handleBudgetBlur"
                :handle-budget-input="handleBudgetInput"
                :handle-delete-custom-budget="handleDeleteCustomBudget"
                :is-hospitality="isHospitality"
                :get-total-q1="getTotalQ1"
                :get-total-q2="getTotalQ2"
                :get-total-q3="getTotalQ3"
                :get-total-q4-sales="getTotalQ4Sales"
                :get-total-q4="getTotalQ4"
                :get-total-sales="getTotalSales"
                :get-total-zero-percent="getTotalZeroPercent"
                :get-zero-percent-rate="getZeroPercentRate"
                :get-total-open-2026="getTotalOpen2026"
                :get-total-q1-budget="getTotalQ1Budget"
                :get-total-q2-budget="getTotalQ2Budget"
                :get-total-q3-budget="getTotalQ3Budget"
                :get-total-q4-budget="getTotalQ4Budget"
                :get-total-budget="getTotalBudget"
            />
        </div>

        <!-- Custom Budget Modal -->
        <AddCustomBudgetModal
            :is-open="addBudgetModal.isOpen.value"
            :is-hospitality="isHospitality"
            :autosuggest-data="autosuggestData"
            @close="closeModal"
            @created="handleCustomBudgetCreated"
            @fetch-autosuggest="handleFetchAutosuggest"
        />
    </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, inject, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useSalesDataForAdmin } from "@/composables/useSalesDataForAdmin";
import { useBudgetDataForAdmin } from "@/composables/useBudgetDataForAdmin";
import SalesTable from "@/components/SalesTable.vue";
import AddCustomBudgetModal from "@/components/AddCustomBudgetModal.vue";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

// Get salesperson ID from route params
const salespersonId = computed(() => {
    const id = route.params.salespersonId;
    return parseInt(id);
});

// Inject modal state and nav actions from App.vue
const addBudgetModal = inject("addBudgetModal");
const navActions = inject("navActions");

// Use admin-specific composables
const {
    sales,
    loading,
    error,
    salespersonInfo,
    isHospitality,
    fetchSales,
        getTotalQ1,
        getTotalQ2,
        getTotalQ3,
        getTotalQ4Sales,
        getTotalQ4,
        getTotalSales,
        getTotalZeroPercent,
        getZeroPercentRate,
        getTotalOpen2026,
} = useSalesDataForAdmin(salespersonId);

const {
    fetchBudgets,
    getBudgetValue,
    getCellClass,
    handleBudgetChange,
    handleBudgetBlur,
    handleBudgetInput,
    loadPendingChangesFromStorage,
    fetchAutosuggestData,
    createCustomBudget,
    deleteCustomBudget,
    getCustomBudgets,
    getTotalQ1Budget,
    getTotalQ2Budget,
    getTotalQ3Budget,
    getTotalQ4Budget,
    getTotalBudget,
    autosuggestData,
    cleanup,
} = useBudgetDataForAdmin(salespersonId);

// Navigation functions
const goBack = () => {
    router.push("/admin");
};

const retryFetch = async () => {
    await fetchSales();
    await fetchBudgets();
};

// Modal handlers
const openModal = () => {
    addBudgetModal.open();
};

const closeModal = () => {
    addBudgetModal.close();
};

const handleCustomBudgetCreated = async (budgetData) => {
    console.log("handleCustomBudgetCreated called with:", budgetData);
    try {
        await createCustomBudget(budgetData);
        console.log("Custom budget created successfully");
    } catch (error) {
        console.error("Error creating custom budget:", error);
    }
};

const handleDeleteCustomBudget = async (budgetId) => {
    try {
        await deleteCustomBudget(budgetId);
        console.log("Custom budget deleted successfully");
    } catch (error) {
        console.error("Error deleting custom budget:", error);
    }
};

const handleFetchAutosuggest = async () => {
    await fetchAutosuggestData();
};

onMounted(async () => {
    // Check if user is admin
    if (!authStore.adminStatus) {
        router.push("/");
        return;
    }

    await fetchSales();
    await fetchBudgets();

    // Load any pending changes from localStorage
    const hasPendingChanges = loadPendingChangesFromStorage();
    if (hasPendingChanges) {
        console.log("Restored pending budget changes from localStorage");
    }

    // Set up navigation actions
    navActions.set([
        {
            id: "back-to-admin",
            text: "Back to Admin",
            class: "btn btn-ghost mr-2",
            handler: goBack,
            icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>',
        },
    ]);

    // Add beforeunload listener to warn about unsaved changes
    window.addEventListener("beforeunload", (event) => {
        // This will be handled by the budget composable
    });
});

onUnmounted(() => {
    window.removeEventListener("beforeunload", () => {});
    navActions.clear();
    cleanup();
});
</script>

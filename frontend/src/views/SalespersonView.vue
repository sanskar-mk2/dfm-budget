<template>
    <div class="salesperson-view">
        <!-- Header with Back Button and Salesperson Info -->
        <div class="header-section">
            <div class="header-content">
                <button @click="goBack" class="back-button">
                    <svg
                        class="back-icon"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M10 19l-7-7m0 0l7-7m-7 7h18"
                        ></path>
                    </svg>
                    Back to Admin Dashboard
                </button>
                <div class="salesperson-info">
                    <h1>
                        Viewing:
                        {{
                            salespersonInfo?.salesperson_name || "Loading..."
                        }}'s Sales & Budget
                    </h1>
                    <p class="role-info">
                        <span
                            class="role-badge"
                            :class="
                                isHospitality
                                    ? 'hospitality'
                                    : 'non-hospitality'
                            "
                        >
                            {{ salespersonInfo?.role || "Unknown Role" }}
                        </span>
                        <span class="salesperson-id"
                            >ID: {{ salespersonInfo?.salesperson_id }}</span
                        >
                    </p>
                </div>
            </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading">
            <div class="spinner"></div>
            <p>Loading salesperson data...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="error">
            <h3>Error Loading Data</h3>
            <p>{{ error }}</p>
            <button @click="retryFetch" class="retry-btn">Retry</button>
        </div>

        <!-- Main Content -->
        <div v-else class="main-content">
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
            />

            <!-- Sales Summary -->
            <SalesSummary
                :sales="sales"
                :get-total-q1="getTotalQ1"
                :get-total-q2="getTotalQ2"
                :get-total-q3="getTotalQ3"
                :get-total-q4="getTotalQ4"
                :get-total-sales="getTotalSales"
                :get-total-zero-percent="getTotalZeroPercent"
                :get-zero-percent-rate="getZeroPercentRate"
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
import SalesSummary from "@/components/SalesSummary.vue";
import AddCustomBudgetModal from "@/components/AddCustomBudgetModal.vue";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

// Get salesperson ID from route params
const salespersonId = computed(() => {
    const id = route.params.salespersonId;
    return parseInt(id);
});

// Inject modal state from App.vue
const addBudgetModal = inject("addBudgetModal");

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
    getTotalQ4,
    getTotalSales,
    getTotalZeroPercent,
    getZeroPercentRate,
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

    // Add beforeunload listener to warn about unsaved changes
    window.addEventListener("beforeunload", (event) => {
        // This will be handled by the budget composable
    });
});

onUnmounted(() => {
    window.removeEventListener("beforeunload", () => {});
    cleanup();
});
</script>

<style scoped>
.salesperson-view {
    padding: 2rem;
    max-width: 100%;
    overflow-x: auto;
}

.header-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    margin: -2rem -2rem 2rem -2rem;
    border-radius: 0 0 1rem 1rem;
}

.header-content {
    display: flex;
    align-items: center;
    gap: 2rem;
}

.back-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;
}

.back-button:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
}

.back-icon {
    width: 1.25rem;
    height: 1.25rem;
}

.salesperson-info h1 {
    margin: 0 0 0.5rem 0;
    font-size: 1.8rem;
    font-weight: 600;
}

.role-info {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 0;
}

.role-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.875rem;
    font-weight: 500;
}

.role-badge.hospitality {
    background-color: #d4edda;
    color: #155724;
}

.role-badge.non-hospitality {
    background-color: #d1ecf1;
    color: #004085;
}

.salesperson-id {
    color: rgba(255, 255, 255, 0.8);
    font-size: 0.9rem;
}

.loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

.error {
    text-align: center;
    padding: 2rem;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 8px;
    color: #721c24;
}

.retry-btn {
    background-color: #dc3545;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 1rem;
}

.retry-btn:hover {
    background-color: #c82333;
}

.main-content {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

@media (max-width: 768px) {
    .salesperson-view {
        padding: 1rem;
    }

    .header-section {
        margin: -1rem -1rem 1rem -1rem;
        padding: 1.5rem;
    }

    .header-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }

    .salesperson-info h1 {
        font-size: 1.5rem;
    }

    .role-info {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
}
</style>

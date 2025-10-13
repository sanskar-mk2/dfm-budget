<script setup>
import { onMounted, onUnmounted, ref, inject } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useSalesData } from '@/composables/useSalesData';
import { useBudgetData } from '@/composables/useBudgetData';
import SalesTable from '@/components/SalesTable.vue';
import SalesSummary from '@/components/SalesSummary.vue';
import UserInfo from '@/components/UserInfo.vue';
import AddCustomBudgetModal from '@/components/AddCustomBudgetModal.vue';

const { currentUser, currentSalesperson } = useAuthStore();

// Inject modal state from App.vue
const addBudgetModal = inject('addBudgetModal');

// Use composables for data management
const {
    sales,
    loading,
    error,
    isHospitality,
    fetchSales,
    getTotalQ1,
    getTotalQ2,
    getTotalQ3,
    getTotalQ4,
    getTotalSales,
    getTotalZeroPercent,
    getZeroPercentRate
} = useSalesData();

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
    cleanup
} = useBudgetData();


// Modal handlers
const openModal = () => {
    addBudgetModal.open();
};

const closeModal = () => {
    addBudgetModal.close();
};

const handleCustomBudgetCreated = async (budgetData) => {
    try {
        await createCustomBudget(budgetData);
        console.log('Custom budget created successfully');
    } catch (error) {
        console.error('Error creating custom budget:', error);
    }
};

const handleDeleteCustomBudget = async (budgetId) => {
    try {
        await deleteCustomBudget(budgetId);
        console.log('Custom budget deleted successfully');
    } catch (error) {
        console.error('Error deleting custom budget:', error);
    }
};

const handleFetchAutosuggest = async () => {
    await fetchAutosuggestData();
};

onMounted(async () => {
    await fetchSales();
    await fetchBudgets();

    // Load any pending changes from localStorage
    const hasPendingChanges = loadPendingChangesFromStorage();
    if (hasPendingChanges) {
        console.log('Restored pending budget changes from localStorage');
    }

    // Add beforeunload listener to warn about unsaved changes
    window.addEventListener('beforeunload', (event) => {
        // This will be handled by the budget composable
    });
});

onUnmounted(() => {
    window.removeEventListener('beforeunload', () => {});
    cleanup();
});
</script>

<template>
    <div class="container mx-auto px-4 py-8">

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

        <!-- User Info -->
        <UserInfo
            :current-user="currentUser"
            :current-salesperson="currentSalesperson"
        />

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

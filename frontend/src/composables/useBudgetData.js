import { ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useSalesData } from "./useSalesData";

export function useBudgetData() {
    const authStore = useAuthStore();
    const { apiCall } = authStore;

    // Get hospitality status from sales data
    const { isHospitality } = useSalesData();

    const budgets = ref([]);
    const budgetMap = ref({});
    const savingCells = ref(new Set());
    const savedCells = ref(new Set());
    const inputValues = ref({});
    const autosuggestData = ref({
        customer_classes: [],
        customer_names: [],
        brands: [],
        flags: [],
    });

    let autoSaveTimer = null;

    const fetchBudgets = async () => {
        try {
            const response = await apiCall("/api/budget");
            if (!response.ok) throw new Error("Failed to fetch budget data");

            const data = await response.json();
            budgets.value = data.data || [];

            // Create map for quick lookup
            budgetMap.value = {};
            budgets.value.forEach((budget) => {
                const key = `${budget.brand || "null"}_${
                    budget.flag || "null"
                }_${budget.customer_name}`;
                budgetMap.value[key] = budget;
            });
        } catch (err) {
            console.error("Error fetching budgets:", err);
        }
    };

    const saveBudgetCell = async (sale, quarter, value) => {
        const cellKey = `${sale.brand || "null"}_${sale.flag || "null"}_${
            sale.customer_name
        }_${quarter}`;
        savingCells.value.add(cellKey);

        try {
            if (!authStore.currentSalesperson) {
                throw new Error("Salesperson data not available");
            }

            const key = `${sale.brand || "null"}_${sale.flag || "null"}_${
                sale.customer_name
            }`;
            const existingBudget = budgetMap.value[key];

            const budgetData = {
                salesperson_id: authStore.currentSalesperson.salesman_no,
                salesperson_name: authStore.currentSalesperson.salesman_name,
                brand: sale.brand,
                flag: sale.flag,
                customer_name: sale.customer_name,
                customer_class: isHospitality.value
                    ? "Hospitality"
                    : sale.derived_customer_class,
                [`quarter_${quarter}_sales`]: parseFloat(value) || 0,
                is_custom: sale.is_custom || false,
            };

            let response;
            if (existingBudget) {
                response = await apiCall(`/api/budget/${existingBudget.id}`, {
                    method: "PUT",
                    body: JSON.stringify({
                        [`quarter_${quarter}_sales`]: parseFloat(value) || 0,
                    }),
                });
            } else {
                response = await apiCall("/api/budget", {
                    method: "POST",
                    body: JSON.stringify(budgetData),
                });
            }

            if (!response.ok) throw new Error("Failed to save budget");

            const result = await response.json();

            // Update local state
            if (existingBudget) {
                existingBudget[`quarter_${quarter}_sales`] =
                    parseFloat(value) || 0;
            } else {
                budgetMap.value[key] = result.data;
                budgets.value.push(result.data);
            }

            // Visual confirmation
            savedCells.value.add(cellKey);
            setTimeout(() => savedCells.value.delete(cellKey), 1000);

            // Clear from localStorage since it's now saved
            savePendingChangesToStorage();
        } catch (err) {
            console.error("Error saving budget:", err);
        } finally {
            savingCells.value.delete(cellKey);
        }
    };

    const getBudgetValue = (sale, quarter) => {
        const cellKey = `${sale.brand || "null"}_${sale.flag || "null"}_${
            sale.customer_name
        }_${quarter}`;

        // Return local input value if it exists (user is typing)
        if (inputValues.value.hasOwnProperty(cellKey)) {
            return inputValues.value[cellKey];
        }

        // Otherwise return from budget data
        const key = `${sale.brand || "null"}_${sale.flag || "null"}_${
            sale.customer_name
        }`;
        const budget = budgetMap.value[key];
        return budget ? budget[`quarter_${quarter}_sales`] || 0 : 0;
    };

    const getCellClass = (sale, quarter) => {
        const cellKey = `${sale.brand || "null"}_${sale.flag || "null"}_${
            sale.customer_name
        }_${quarter}`;
        if (savingCells.value.has(cellKey)) return "bg-blue-50 border-blue-300";
        if (savedCells.value.has(cellKey))
            return "bg-green-50 border-green-300";
        return "hover:bg-gray-50";
    };

    const scheduleAutoSave = (sale, quarter, value) => {
        if (autoSaveTimer) {
            clearTimeout(autoSaveTimer);
        }

        autoSaveTimer = setTimeout(() => {
            if (value && value !== "0" && value !== "") {
                saveBudgetCell(sale, quarter, value);
            }
        }, 2000);
    };

    const handleBudgetChange = (event, sale, quarter) => {
        const cellKey = `${sale.brand || "null"}_${sale.flag || "null"}_${
            sale.customer_name
        }_${quarter}`;
        const value = event.target.value;
        inputValues.value[cellKey] = value;

        savePendingChangesToStorage();
        scheduleAutoSave(sale, quarter, value);
    };

    const handleBudgetBlur = (event, sale, quarter) => {
        const value = event.target.value;
        const cellKey = `${sale.brand || "null"}_${sale.flag || "null"}_${
            sale.customer_name
        }_${quarter}`;

        if (autoSaveTimer) {
            clearTimeout(autoSaveTimer);
            autoSaveTimer = null;
        }

        delete inputValues.value[cellKey];
        savePendingChangesToStorage();
        saveBudgetCell(sale, quarter, value);
    };

    const handleBudgetInput = (event, sale, quarter) => {
        const cellKey = `${sale.brand || "null"}_${sale.flag || "null"}_${
            sale.customer_name
        }_${quarter}`;
        inputValues.value[cellKey] = event.target.value;

        if (event.key === "Enter") {
            event.target.blur();
        }
    };

    const savePendingChangesToStorage = () => {
        const pendingChanges = {};
        Object.keys(inputValues.value).forEach((cellKey) => {
            const value = inputValues.value[cellKey];
            if (value && value !== "0" && value !== "") {
                pendingChanges[cellKey] = value;
            }
        });
        localStorage.setItem(
            "budget_pending_changes",
            JSON.stringify(pendingChanges)
        );
    };

    const loadPendingChangesFromStorage = () => {
        try {
            const stored = localStorage.getItem("budget_pending_changes");
            if (stored) {
                const pendingChanges = JSON.parse(stored);
                Object.keys(pendingChanges).forEach((cellKey) => {
                    inputValues.value[cellKey] = pendingChanges[cellKey];
                });
                return Object.keys(pendingChanges).length > 0;
            }
        } catch (err) {
            console.error("Error loading pending changes:", err);
        }
        return false;
    };

    const clearPendingChangesFromStorage = () => {
        localStorage.removeItem("budget_pending_changes");
    };

    const fetchAutosuggestData = async () => {
        try {
            const response = await apiCall("/api/budget/autosuggest");
            if (!response.ok)
                throw new Error("Failed to fetch autosuggest data");

            const data = await response.json();
            autosuggestData.value = data.data;
        } catch (err) {
            console.error("Error fetching autosuggest data:", err);
        }
    };

    const createCustomBudget = async (budgetData) => {
        try {
            if (!authStore.currentSalesperson) {
                throw new Error("Salesperson data not available");
            }

            const customBudgetData = {
                ...budgetData,
                salesperson_id: authStore.currentSalesperson.salesman_no,
                salesperson_name: authStore.currentSalesperson.salesman_name,
                customer_class: isHospitality.value
                    ? "Hospitality"
                    : budgetData.customer_class,
                quarter_1_sales: 0,
                quarter_2_sales: 0,
                quarter_3_sales: 0,
                quarter_4_sales: 0,
                is_custom: true,
            };

            const response = await apiCall("/api/budget", {
                method: "POST",
                body: JSON.stringify(customBudgetData),
            });

            if (!response.ok) throw new Error("Failed to create custom budget");

            const result = await response.json();

            // Add to local state
            const key = `${customBudgetData.brand || "null"}_${
                customBudgetData.flag || "null"
            }_${customBudgetData.customer_name}`;
            budgetMap.value[key] = result.data;
            budgets.value.push(result.data);

            return result.data;
        } catch (err) {
            console.error("Error creating custom budget:", err);
            throw err;
        }
    };

    const deleteCustomBudget = async (budgetId) => {
        try {
            const response = await apiCall(`/api/budget/${budgetId}`, {
                method: "DELETE",
            });

            if (!response.ok) throw new Error("Failed to delete custom budget");

            // Remove from local state
            const budgetIndex = budgets.value.findIndex(
                (b) => b.id === budgetId
            );
            if (budgetIndex !== -1) {
                const budget = budgets.value[budgetIndex];
                const key = `${budget.brand || "null"}_${
                    budget.flag || "null"
                }_${budget.customer_name}`;
                delete budgetMap.value[key];
                budgets.value.splice(budgetIndex, 1);
            }

            return true;
        } catch (err) {
            console.error("Error deleting custom budget:", err);
            throw err;
        }
    };

    const getCustomBudgets = () => {
        return budgets.value.filter((budget) => budget.is_custom === true);
    };

    // Budget summary calculation functions
    const getTotalQ1Budget = () => {
        return budgets.value.reduce(
            (sum, budget) => sum + (parseFloat(budget.quarter_1_sales) || 0),
            0
        );
    };

    const getTotalQ2Budget = () => {
        return budgets.value.reduce(
            (sum, budget) => sum + (parseFloat(budget.quarter_2_sales) || 0),
            0
        );
    };

    const getTotalQ3Budget = () => {
        return budgets.value.reduce(
            (sum, budget) => sum + (parseFloat(budget.quarter_3_sales) || 0),
            0
        );
    };

    const getTotalQ4Budget = () => {
        return budgets.value.reduce(
            (sum, budget) => sum + (parseFloat(budget.quarter_4_sales) || 0),
            0
        );
    };

    const getTotalBudget = () => {
        return budgets.value.reduce(
            (sum, budget) => sum + (parseFloat(budget.total_sales) || 0),
            0
        );
    };

    const cleanup = () => {
        if (autoSaveTimer) {
            clearTimeout(autoSaveTimer);
        }
    };

    return {
        budgets,
        budgetMap,
        savingCells,
        savedCells,
        inputValues,
        autosuggestData,
        fetchBudgets,
        saveBudgetCell,
        getBudgetValue,
        getCellClass,
        handleBudgetChange,
        handleBudgetBlur,
        handleBudgetInput,
        savePendingChangesToStorage,
        loadPendingChangesFromStorage,
        clearPendingChangesFromStorage,
        fetchAutosuggestData,
        createCustomBudget,
        deleteCustomBudget,
        getCustomBudgets,
        getTotalQ1Budget,
        getTotalQ2Budget,
        getTotalQ3Budget,
        getTotalQ4Budget,
        getTotalBudget,
        cleanup,
    };
}

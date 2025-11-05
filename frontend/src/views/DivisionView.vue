<script setup>
import { onMounted, onUnmounted, inject, computed, reactive, watch } from "vue";
import { storeToRefs } from "pinia";
import { useDivisionData } from "@/composables/useDivisionData";
import DivisionGroupCard from "@/components/DivisionGroupCard.vue";
import LoadingError from "@/components/LoadingError.vue";
import { useAuthStore } from "@/stores/auth";
import { downloadCSV, formatCurrencyForCSV } from "@/utils/downloadUtils";

const navActions = inject("navActions");
const {
    loading,
    error,
    groupedData,
    fetchDivisionData,
    saveRatios,
    resetGroupOverrides,
    resetAllOverrides,
} = useDivisionData();
const authStore = useAuthStore();
const { adminStatus, superadminStatus } = storeToRefs(authStore);

const handleSaveRatios = async (groupKey, divisions) => {
    try {
        await saveRatios(groupKey, divisions);
    } catch (error) {
        console.error("Error saving ratios:", error);
        // You might want to show a toast notification here
    }
};

const handleResetGroup = async (salespersonId, customerClass, groupKey) => {
    try {
        await resetGroupOverrides(salespersonId, customerClass, groupKey);
    } catch (error) {
        console.error("Error resetting group overrides:", error);
    }
};

const handleResetAll = async () => {
    try {
        await resetAllOverrides();
    } catch (error) {
        console.error("Error resetting overrides:", error);
    }
};

const resetAllAction = {
    id: "reset-all-overrides",
    text: "Reset All Overrides",
    class: "btn btn-warning mr-2",
    handler: handleResetAll,
    icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>',
};

const backAction = {
    id: "back-to-admin",
    text: "Back to Admin",
    class: "btn btn-ghost",
    handler: () => {
        // Navigate back to admin view
        window.history.back();
    },
    icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>',
};

// CSV Export functionality - defined early so it can be used in updateNavActions
const prepareDataForCSV = () => {
    if (!groupedData.value?.length) return [];
    
    const csvRows = [];
    
    groupedData.value.forEach((group) => {
        // If group has divisions, create a row for each division
        if (group.divisions && group.divisions.length > 0) {
            group.divisions.forEach((division) => {
                csvRows.push({
                    salesperson_name: group.salesperson_name,
                    salesperson_id: group.salesperson_id,
                    customer_class: group.customer_class,
                    group_key: group.group_key,
                    brand: group.brand || "",
                    has_custom_ratios: group.hasCustomRatios ? "Yes" : "No",
                    item_division: division.item_division,
                    division_name: division.division_name || "",
                    division_ratio_2025: division.division_ratio_2025 != null ? ((division.division_ratio_2025 * 100).toFixed(2) + "%") : "",
                    effective_ratio: division.effective_ratio != null ? ((division.effective_ratio * 100).toFixed(2) + "%") : "",
                    is_custom: division.is_custom ? "Yes" : "No",
                    total_2025_sales: formatCurrencyForCSV(division.total_2025_sales || 0),
                    q1_allocated: formatCurrencyForCSV(division.q1_allocated || 0),
                    q2_allocated: formatCurrencyForCSV(division.q2_allocated || 0),
                    q3_allocated: formatCurrencyForCSV(division.q3_allocated || 0),
                    q4_allocated: formatCurrencyForCSV(division.q4_allocated || 0),
                    total_allocated: formatCurrencyForCSV(division.total_allocated || 0),
                });
            });
        } else {
            // If no divisions, still create a row with group info
            csvRows.push({
                salesperson_name: group.salesperson_name,
                salesperson_id: group.salesperson_id,
                customer_class: group.customer_class,
                group_key: group.group_key,
                brand: group.brand || "",
                has_custom_ratios: group.hasCustomRatios ? "Yes" : "No",
                item_division: "",
                division_name: "",
                division_ratio_2025: "",
                effective_ratio: "",
                is_custom: "",
                total_2025_sales: "",
                q1_allocated: "",
                q2_allocated: "",
                q3_allocated: "",
                q4_allocated: "",
                total_allocated: "",
            });
        }
    });
    
    return csvRows;
};

const getCSVHeaders = () => [
    { key: 'salesperson_name', label: 'Salesperson Name' },
    { key: 'salesperson_id', label: 'Salesperson ID' },
    { key: 'customer_class', label: 'Customer Class' },
    { key: 'group_key', label: 'Group Key' },
    { key: 'brand', label: 'Brand' },
    { key: 'has_custom_ratios', label: 'Has Custom Ratios' },
    { key: 'item_division', label: 'Item Division' },
    { key: 'division_name', label: 'Division Name' },
    { key: 'division_ratio_2025', label: '2025 Division Ratio' },
    { key: 'effective_ratio', label: 'Effective Ratio' },
    { key: 'is_custom', label: 'Is Custom' },
    { key: 'total_2025_sales', label: 'Total 2025 Sales' },
    { key: 'q1_allocated', label: 'Q1 Allocated' },
    { key: 'q2_allocated', label: 'Q2 Allocated' },
    { key: 'q3_allocated', label: 'Q3 Allocated' },
    { key: 'q4_allocated', label: 'Q4 Allocated' },
    { key: 'total_allocated', label: 'Total Allocated' },
];

const handleExportCSV = () => {
    const data = prepareDataForCSV();
    if (!data.length) {
        alert("No data available to export");
        return;
    }
    
    const headers = getCSVHeaders();
    const filename = `division_ratios_${new Date().toISOString().split("T")[0]}.csv`;
    downloadCSV(data, headers, filename);
};

const exportAction = {
    id: "export-csv",
    text: "Export to CSV",
    class: "btn btn-primary mr-2",
    handler: handleExportCSV,
    icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>',
};

const updateNavActions = () => {
    const actions = [];
    if (adminStatus.value || superadminStatus.value) {
        actions.push(exportAction);
    }
    if (superadminStatus.value) {
        actions.push(resetAllAction);
    }
    if (adminStatus.value || superadminStatus.value) {
        actions.push(backAction);
    }
    navActions.set(actions);
};

watch([adminStatus, superadminStatus], () => updateNavActions(), {
    immediate: true,
});

const expandedGroups = reactive({});

const makeGroupKey = (group) =>
    `${group.salesperson_id}-${group.customer_class}-${group.group_key}`;

const computeSummary = (group) => {
    return group.divisions.reduce(
        (acc, division) => {
            acc.totalRatio += division.effective_ratio || 0;
            acc.totalSales += division.total_2025_sales || 0;
            acc.q1 += division.q1_allocated || 0;
            acc.q2 += division.q2_allocated || 0;
            acc.q3 += division.q3_allocated || 0;
            acc.q4 += division.q4_allocated || 0;
            acc.grandTotal += division.total_allocated || 0;
            return acc;
        },
        {
            totalRatio: 0,
            totalSales: 0,
            q1: 0,
            q2: 0,
            q3: 0,
            q4: 0,
            grandTotal: 0,
        }
    );
};

const groupRows = computed(() => {
    if (!groupedData.value || groupedData.value.length === 0) {
        return [];
    }

    return groupedData.value.map((group) => {
        const key = makeGroupKey(group);
        return {
            key,
            group,
            summary: computeSummary(group),
            label: `${group.customer_class} > ${group.salesperson_name} > ${group.display_key}`,
        };
    });
});

const toggleGroup = (key) => {
    expandedGroups[key] = !expandedGroups[key];
};

const formatCurrency = (value) => {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value || 0);
};

const formatPercent = (value) => `${((value || 0) * 100).toFixed(1)}%`;

onMounted(() => {
    updateNavActions();
    // Fetch division data when component mounts
    fetchDivisionData();
});

onUnmounted(() => navActions.clear());
</script>

<template>
    <div class="p-6 space-y-6">
        <!-- Header -->
        <!-- <div class="hero bg-base-200 rounded-lg">
            <div class="hero-content text-center">
                <div class="max-w-4xl">
                    <h1 class="text-5xl font-bold">Division Ratio Management</h1>
                    <p class="py-6">
                        Adjust division ratios for budget allocation. Use sliders to modify ratios and lock divisions to prevent changes.
                    </p>
                </div>
            </div>
        </div> -->

        <!-- Loading and Error States -->
        <LoadingError
            :loading="loading"
            :error="error"
            @retry="fetchDivisionData"
        />

        <!-- Division Groups -->
        <div
            v-if="!loading && !error && groupRows.length > 0"
            class="space-y-6"
        >
            <div class="stats shadow mb-6">
                <div class="stat">
                    <div class="stat-title">Module</div>
                    <div class="stat-value text-primary">
                        Division Ratio Management
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Total Groups</div>
                    <div class="stat-value text-primary">
                        {{ groupedData.length }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Groups with Custom Ratios</div>
                    <div class="stat-value text-secondary">
                        {{
                            groupedData.filter((g) => g.hasCustomRatios).length
                        }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Total Divisions</div>
                    <div class="stat-value text-accent">
                        {{
                            groupedData.reduce(
                                (sum, g) => sum + g.divisions.length,
                                0
                            )
                        }}
                    </div>
                </div>
            </div>

            <div class="overflow-x-auto">
                <table class="table table-zebra w-full">
                    <thead>
                        <tr>
                            <th class="w-20">Action</th>
                            <th>Group</th>
                            <th class="text-right">Total Ratio</th>
                            <th class="text-right">Total Sales</th>
                            <th class="text-right">Q1 Budget</th>
                            <th class="text-right">Q2 Budget</th>
                            <th class="text-right">Q3 Budget</th>
                            <th class="text-right">Q4 Budget</th>
                            <th class="text-right">Grand Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="row in groupRows" :key="row.key">
                            <tr>
                                <td>
                                    <button
                                        class="btn btn-outline btn-xs"
                                        type="button"
                                        @click="toggleGroup(row.key)"
                                    >
                                        {{
                                            expandedGroups[row.key]
                                                ? "Collapse"
                                                : "Expand"
                                        }}
                                    </button>
                                </td>
                                <td>
                                    <div class="font-semibold">
                                        {{ row.group.display_key }}
                                    </div>
                                    <div class="text-xs opacity-70">
                                        {{ row.group.customer_class }} •
                                        {{ row.group.salesperson_name }}
                                    </div>
                                </td>
                                <td class="text-right font-mono">
                                    {{ formatPercent(row.summary.totalRatio) }}
                                </td>
                                <td class="text-right font-mono">
                                    {{ formatCurrency(row.summary.totalSales) }}
                                </td>
                                <td class="text-right font-mono">
                                    {{ formatCurrency(row.summary.q1) }}
                                </td>
                                <td class="text-right font-mono">
                                    {{ formatCurrency(row.summary.q2) }}
                                </td>
                                <td class="text-right font-mono">
                                    {{ formatCurrency(row.summary.q3) }}
                                </td>
                                <td class="text-right font-mono">
                                    {{ formatCurrency(row.summary.q4) }}
                                </td>
                                <td class="text-right font-mono font-semibold">
                                    {{ formatCurrency(row.summary.grandTotal) }}
                                </td>
                            </tr>
                            <tr v-if="expandedGroups[row.key]">
                                <!-- <td></td> -->
                                <td colspan="100%">
                                    <DivisionGroupCard
                                        :group="row.group"
                                        @save-ratios="handleSaveRatios"
                                        @reset-group="handleResetGroup"
                                        @collapse="toggleGroup(row.key)"
                                    />
                                </td>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- No Data State -->
        <div
            v-if="!loading && !error && groupedData.length === 0"
            class="alert alert-info"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                class="stroke-current shrink-0 w-6 h-6"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
            </svg>
            <span
                >No division data available. Please check your data
                sources.</span
            >
        </div>
    </div>
</template>

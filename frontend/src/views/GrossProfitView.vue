<script setup>
import { onMounted, onUnmounted, inject, computed, reactive, watch } from "vue";
import { storeToRefs } from "pinia";
import { useGrossProfitData } from "@/composables/useGrossProfitData";
import GrossProfitGroupCard from "@/components/GrossProfitGroupCard.vue";
import LoadingError from "@/components/LoadingError.vue";
import { useAuthStore } from "@/stores/auth";
import { downloadCSV, formatCurrencyForCSV } from "@/utils/downloadUtils";

const navActions = inject("navActions");
const { grouped, fetch, save, reset, resetAll, loading } = useGrossProfitData();
const authStore = useAuthStore();
const { adminStatus, superadminStatus } = storeToRefs(authStore);

const handleResetAll = async () => {
    try {
        await resetAll();
    } catch (error) {
        console.error("Error resetting all overrides:", error);
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
    if (!grouped.value?.length) return [];
    
    return grouped.value.map((group) => {
        const q1 = group.quarters.find(q => q.label === "Q1");
        const q2 = group.quarters.find(q => q.label === "Q2");
        const q3 = group.quarters.find(q => q.label === "Q3");
        const q4 = group.quarters.find(q => q.label === "Q4");
        
        const total2025Sales = (q1?.sales_2025 || 0) + (q2?.sales_2025 || 0) + (q3?.sales_2025 || 0) + (q4?.sales_2025 || 0);
        const total2026Budget = (q1?.sales || 0) + (q2?.sales || 0) + (q3?.sales || 0) + (q4?.sales || 0);
        const totalGpValue = (q1?.gp_value || 0) + (q2?.gp_value || 0) + (q3?.gp_value || 0) + (q4?.gp_value || 0);
        
        return {
            salesperson_name: group.salesperson_name,
            salesperson_id: group.salesperson_id,
            customer_class: group.customer_class,
            group_key: group.group_key,
            brand: group.brand || "",
            // 2025 Sales
            q1_2025_sales: formatCurrencyForCSV(q1?.sales_2025 || 0),
            q2_2025_sales: formatCurrencyForCSV(q2?.sales_2025 || 0),
            q3_2025_sales: formatCurrencyForCSV(q3?.sales_2025 || 0),
            q4_2025_sales: formatCurrencyForCSV(q4?.sales_2025 || 0),
            total_2025_sales: formatCurrencyForCSV(total2025Sales),
            // 2026 Budget
            q1_2026_budget: formatCurrencyForCSV(q1?.sales || 0),
            q2_2026_budget: formatCurrencyForCSV(q2?.sales || 0),
            q3_2026_budget: formatCurrencyForCSV(q3?.sales || 0),
            q4_2026_budget: formatCurrencyForCSV(q4?.sales || 0),
            total_2026_budget: formatCurrencyForCSV(total2026Budget),
            // Historical GP%
            q1_historical_gp_percent: q1?.gp_percent != null ? ((q1.gp_percent * 100).toFixed(2) + "%") : "",
            q2_historical_gp_percent: q2?.gp_percent != null ? ((q2.gp_percent * 100).toFixed(2) + "%") : "",
            q3_historical_gp_percent: q3?.gp_percent != null ? ((q3.gp_percent * 100).toFixed(2) + "%") : "",
            q4_historical_gp_percent: q4?.gp_percent != null ? ((q4.gp_percent * 100).toFixed(2) + "%") : "",
            // Effective GP%
            q1_effective_gp_percent: q1?.effective_gp_percent != null ? ((q1.effective_gp_percent * 100).toFixed(2) + "%") : "",
            q2_effective_gp_percent: q2?.effective_gp_percent != null ? ((q2.effective_gp_percent * 100).toFixed(2) + "%") : "",
            q3_effective_gp_percent: q3?.effective_gp_percent != null ? ((q3.effective_gp_percent * 100).toFixed(2) + "%") : "",
            q4_effective_gp_percent: q4?.effective_gp_percent != null ? ((q4.effective_gp_percent * 100).toFixed(2) + "%") : "",
            full_year_effective_gp_percent: group.effective_gp_percent != null ? ((group.effective_gp_percent * 100).toFixed(2) + "%") : "",
            // GP Values
            q1_gp_value: formatCurrencyForCSV(q1?.gp_value || 0),
            q2_gp_value: formatCurrencyForCSV(q2?.gp_value || 0),
            q3_gp_value: formatCurrencyForCSV(q3?.gp_value || 0),
            q4_gp_value: formatCurrencyForCSV(q4?.gp_value || 0),
            total_gp_value: formatCurrencyForCSV(totalGpValue),
            // Flags
            has_custom_overrides: group.is_custom ? "Yes" : "No",
        };
    });
};

const getCSVHeaders = () => [
    { key: 'salesperson_name', label: 'Salesperson Name' },
    { key: 'salesperson_id', label: 'Salesperson ID' },
    { key: 'customer_class', label: 'Customer Class' },
    { key: 'group_key', label: 'Group Key' },
    { key: 'brand', label: 'Brand' },
    { key: 'q1_2025_sales', label: 'Q1 2025 Sales' },
    { key: 'q2_2025_sales', label: 'Q2 2025 Sales' },
    { key: 'q3_2025_sales', label: 'Q3 2025 Sales' },
    { key: 'q4_2025_sales', label: 'Q4 2025 Sales' },
    { key: 'total_2025_sales', label: 'Total 2025 Sales' },
    { key: 'q1_2026_budget', label: 'Q1 2026 Budget' },
    { key: 'q2_2026_budget', label: 'Q2 2026 Budget' },
    { key: 'q3_2026_budget', label: 'Q3 2026 Budget' },
    { key: 'q4_2026_budget', label: 'Q4 2026 Budget' },
    { key: 'total_2026_budget', label: 'Total 2026 Budget' },
    { key: 'q1_historical_gp_percent', label: 'Q1 Historical GP%' },
    { key: 'q2_historical_gp_percent', label: 'Q2 Historical GP%' },
    { key: 'q3_historical_gp_percent', label: 'Q3 Historical GP%' },
    { key: 'q4_historical_gp_percent', label: 'Q4 Historical GP%' },
    { key: 'q1_effective_gp_percent', label: 'Q1 Effective GP%' },
    { key: 'q2_effective_gp_percent', label: 'Q2 Effective GP%' },
    { key: 'q3_effective_gp_percent', label: 'Q3 Effective GP%' },
    { key: 'q4_effective_gp_percent', label: 'Q4 Effective GP%' },
    { key: 'full_year_effective_gp_percent', label: 'Full Year Effective GP%' },
    { key: 'q1_gp_value', label: 'Q1 GP Value' },
    { key: 'q2_gp_value', label: 'Q2 GP Value' },
    { key: 'q3_gp_value', label: 'Q3 GP Value' },
    { key: 'q4_gp_value', label: 'Q4 GP Value' },
    { key: 'total_gp_value', label: 'Total GP Value' },
    { key: 'has_custom_overrides', label: 'Has Custom Overrides' },
];

const handleExportCSV = () => {
    const data = prepareDataForCSV();
    if (!data.length) {
        alert("No data available to export");
        return;
    }
    
    const headers = getCSVHeaders();
    const filename = `gross_profit_${new Date().toISOString().split("T")[0]}.csv`;
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
    const totals = group.quarters.reduce(
        (acc, quarter) => {
            acc.sales2025 += quarter.sales_2025 || 0;
            acc.budget2026 += quarter.sales || 0;
            acc.gpValue += quarter.gp_value || 0;
            return acc;
        },
        { sales2025: 0, budget2026: 0, gpValue: 0 }
    );

    return {
        ...totals,
        effectiveGp: group.effective_gp_percent || 0,
    };
};

const groupRows = computed(() => {
    if (!grouped.value?.length) {
        return [];
    }

    return grouped.value.map((group) => {
        const key = makeGroupKey(group);
        return {
            key,
            group,
            summary: computeSummary(group),
        };
    });
});

const averageGpPercent = computed(() => {
    if (!grouped.value?.length) {
        return 0;
    }
    const total = grouped.value.reduce(
        (sum, grp) => sum + (grp.effective_gp_percent || 0),
        0
    );
    return total / grouped.value.length;
});

const toggleGroup = (key) => {
    expandedGroups[key] = !expandedGroups[key];
};

const formatCurrency = (value) =>
    new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value || 0);

const formatPercent = (value) => `${((value || 0) * 100).toFixed(1)}%`;

onMounted(() => {
    updateNavActions();
    // Fetch gross profit data when component mounts
    fetch();
});

onUnmounted(() => navActions.clear());
</script>

<template>
    <div class="p-6 space-y-6">
        <!-- Header -->
        <!-- <div class="hero bg-base-200 rounded-lg">
            <div class="hero-content text-center">
                <div class="max-w-4xl">
                    <h1 class="text-5xl font-bold">Gross Profit Management</h1>
                    <p class="py-6">
                        Adjust effective GP% overrides for budget allocation.
                        Use sliders to modify gross profit percentages and save
                        changes.
                    </p>
                </div>
            </div>
        </div> -->

        <!-- Loading and Error States -->
        <LoadingError :loading="loading" :error="null" @retry="fetch" />

        <!-- Stats Summary -->
        <div v-if="!loading && grouped.length > 0" class="stats shadow mb-6">
            <div class="stat">
                <div class="stat-title">Module</div>
                <div class="stat-value text-primary">
                    Gross Profit Management
                </div>
            </div>
            <div class="stat">
                <div class="stat-title">Total Groups</div>
                <div class="stat-value text-primary">{{ grouped.length }}</div>
            </div>
            <div class="stat">
                <div class="stat-title">Groups with Custom GP%</div>
                <div class="stat-value text-secondary">
                    {{ grouped.filter((g) => g.is_custom).length }}
                </div>
            </div>
            <div class="stat">
                <div class="stat-title">Average GP%</div>
                <div class="stat-value text-accent">
                    {{ formatPercent(averageGpPercent) }}
                </div>
            </div>
        </div>

        <!-- Gross Profit Groups -->
        <div v-if="!loading && groupRows.length > 0">
            <div class="overflow-x-auto">
                <table class="table table-zebra w-full">
                    <thead>
                        <tr>
                            <th class="w-20">Action</th>
                            <th>Group</th>
                            <th class="text-right">2025 Sales</th>
                            <th class="text-right">2026 Budget</th>
                            <th class="text-right">Historical GP%</th>
                            <th class="text-right">GP $ Est.</th>
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
                                        {{ row.group.customer_class }} -
                                        {{ row.group.salesperson_name }}
                                    </div>
                                </td>
                                <td class="text-right font-mono">
                                    {{ formatCurrency(row.summary.sales2025) }}
                                </td>
                                <td class="text-right font-mono">
                                    {{ formatCurrency(row.summary.budget2026) }}
                                </td>
                                <td class="text-right font-mono">
                                    {{ formatPercent(row.summary.effectiveGp) }}
                                </td>
                                <td class="text-right font-mono font-semibold">
                                    {{ formatCurrency(row.summary.gpValue) }}
                                </td>
                            </tr>
                            <tr v-if="expandedGroups[row.key]">
                                <!-- <td></td> -->
                                <td colspan="100%">
                                    <GrossProfitGroupCard
                                        :group="row.group"
                                        :onSave="save"
                                        :onReset="reset"
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
            v-else-if="!loading && grouped.length === 0"
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
                >No gross profit data available. Please check your data
                sources.</span
            >
        </div>
    </div>
</template>

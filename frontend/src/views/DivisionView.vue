<script setup>
import { onMounted, onUnmounted, inject, computed, reactive } from "vue";
import { useDivisionData } from "@/composables/useDivisionData";
import DivisionGroupCard from "@/components/DivisionGroupCard.vue";
import LoadingError from "@/components/LoadingError.vue";

const navActions = inject("navActions");
const { loading, error, groupedData, fetchDivisionData, saveRatios, resetGroupOverrides, resetAllOverrides } = useDivisionData();

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
    // Set navigation actions for this view
    navActions.set([
        {
            id: "reset-all-overrides",
            text: "Reset All Overrides",
            class: "btn btn-warning mr-2",
            handler: handleResetAll,
            icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>',
        },
        {
            id: "back-to-admin",
            text: "Back to Admin",
            class: "btn btn-ghost",
            handler: () => {
                // Navigate back to admin view
                window.history.back();
            },
            icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>',
        },
    ]);
    
    // Fetch division data when component mounts
    fetchDivisionData();
});

onUnmounted(() => navActions.clear());
</script>

<template>
    <div class="p-6 space-y-6">
        <!-- Header -->
        <div class="hero bg-base-200 rounded-lg">
            <div class="hero-content text-center">
                <div class="max-w-4xl">
                    <h1 class="text-5xl font-bold">Division Ratio Management</h1>
                    <p class="py-6">
                        Adjust division ratios for budget allocation. Use sliders to modify ratios and lock divisions to prevent changes.
                    </p>
                </div>
            </div>
        </div>

        <!-- Loading and Error States -->
        <LoadingError 
            :loading="loading" 
            :error="error" 
            @retry="fetchDivisionData" 
        />

        <!-- Division Groups -->
        <div v-if="!loading && !error && groupRows.length > 0" class="space-y-6">
            <div class="stats shadow mb-6">
                <div class="stat">
                    <div class="stat-title">Total Groups</div>
                    <div class="stat-value text-primary">{{ groupedData.length }}</div>
                </div>
                <div class="stat">
                    <div class="stat-title">Groups with Custom Ratios</div>
                    <div class="stat-value text-secondary">
                        {{ groupedData.filter(g => g.hasCustomRatios).length }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Total Divisions</div>
                    <div class="stat-value text-accent">
                        {{ groupedData.reduce((sum, g) => sum + g.divisions.length, 0) }}
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
                                        {{ expandedGroups[row.key] ? "Collapse" : "Expand" }}
                                    </button>
                                </td>
                                <td>
                                    <div class="font-semibold">{{ row.group.display_key }}</div>
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
                                <td></td>
                                <td colspan="8">
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
        <div v-else-if="!loading && !error && groupedData.length === 0" class="alert alert-info">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>No division data available. Please check your data sources.</span>
        </div>
    </div>
</template>
